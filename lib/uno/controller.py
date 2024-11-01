from lib.uno.models import UnoCard, UnoException, UnoGameState, UnoMessage
from lib.uno.views import UnoEmptyView, UnoView, UnoGameView, UnoHandView, UnoLobbyView, UnoMenuView, UnoWildMenuView

import asyncio


class UnoController:
    """ Uno game controller.

    Handles user input, updates game models, and provides responses.

    Validates form of user input; leaves logic and relational validation to the game model.
    """
    def __init__(self, parent_cog, channel_id):
        self.lock       = asyncio.Lock()
        self.parent_cog = parent_cog
        self.channel_id = channel_id

        self.gamestate = UnoGameState(self)
        self.active_views = []

        self.reminder    = UnoEmptyView()
        self.draw_notice = UnoEmptyView()

        self._activity_flag = asyncio.Event()
        self._timeout_check = asyncio.create_task(self._check_timeout())

    async def update_views(self, *view_types, check=None):
        if not view_types:
            view_types = UnoView

        for view in self.active_views:
            if isinstance(view, view_types):
                if not check or check(view):
                    await view.update()

    # use this decorator on all user interaction in this class -- otherwise, timeout will happen early.
    def _is_activity(func):
        def internal(self, *args, **kwargs):
            self._activity_flag.set()
            return func(self, *args, **kwargs)
        return internal
    
    def _build_reminder(self, msg, on_death=None):
        if self.reminder.message:
            asyncio.create_task(self.reminder.die())
        self.reminder = UnoEmptyView(on_death)
        return UnoMessage(msg, self.reminder)

    @_is_activity
    def get_lobby_msg(self):
        # kill old lobby views (doesn't make sense to have multiple)
        for view in self.active_views:
            if isinstance(view, UnoLobbyView):
                asyncio.create_task(view.die())

        lobby_view = UnoLobbyView(self.gamestate, self)
        self.active_views.append(lobby_view)
        return UnoMessage.from_uno_view(lobby_view)

    @_is_activity
    def join(self, player):
        try:
            self.gamestate.add_player(player)
            msg = UnoMessage(f"{player.mention} has joined the lobby!")
        except UnoException as err:
            msg = UnoMessage(str(err), is_ephemeral=True)

        asyncio.create_task(self.update_views(UnoLobbyView))
        return msg

    def leave(self, player):
        try:
            next_player = self.gamestate.remove_player(player)
            msg = f"{player.mention} has left the lobby. "

            msg = UnoMessage(msg)
        except UnoException as err:
            msg = UnoMessage(str(err), is_ephemeral=True)

        # end game if relevant
        if not self.gamestate.in_game:
            reason = next_player
            asyncio.create_task(self.die(reason, send_message=False))
            return UnoMessage(reason)

        if next_player:
            msg += f"{next_player.mention}, it's your turn!"

        asyncio.create_task(self.update_views(UnoLobbyView, UnoMenuView))
        for view in self.active_views:
            if isinstance(view, UnoHandView):
                if view.player == player:
                    asyncio.create_task(view.die("You left the game."))
                elif next_player and view.player == next_player:
                    asyncio.create_task(view.update())
        return msg

    @_is_activity
    def start_game(self, player):
        # TODO consider adding a relative timestamp <t:unix_time:R> as a "countdown"
        if player not in self.gamestate.players:
            return UnoMessage("Let the players start their game themselves!", is_ephemeral=True)
        try:
            self.gamestate.start_game()

            view = UnoGameView(self.gamestate, self)
            self.active_views.append(view)

            msg = UnoMessage.from_uno_view(view)
            msg.content = f"The Uno game has started!\n\n{msg.content}"
        except UnoException as err:
            msg = UnoMessage(str(err), is_ephemeral=True)

        for view in self.active_views:
            if isinstance(view, UnoLobbyView):
                asyncio.create_task(view.die())
        return msg

    @_is_activity
    def get_gamestate_msg(self):
        game_view = UnoGameView(self.gamestate, self)
        self.active_views.append(game_view)
        return UnoMessage.from_uno_view(game_view)

    @_is_activity
    def get_menu_msg(self, player):
        menu_view = UnoMenuView(self.gamestate, self, player)
        self.active_views.append(menu_view)
        return UnoMessage.from_uno_view(menu_view, is_ephemeral=True)

    @_is_activity
    def votekick(self, player, target):
        try:
            kick_added, votekicks, threshold, next_player = self.gamestate.votekick(player, target)
        except UnoException as err:
            return UnoMessage(str(err), is_ephemeral=True)

        # end game if relevant
        if not self.gamestate.in_game:
            reason = next_player # kind of feels dirty repurposing the return value, but hey
            asyncio.create_task(self.die(reason, send_message=False))
            return UnoMessage(reason)

        if not kick_added:
            msg  = f"{player.mention} has removed their votekick from {target.mention}. "
            msg += f"{votekicks} / {threshold} kick votes received."
        else:
            msg  = f"{player.mention} has voted to kick {target.mention}. "
            if votekicks >= threshold:
                msg += f"{target.mention} has been kicked from the game!"
            else:
                msg += f"{votekicks} / {threshold} kick votes received."
            
            if next_player:
                msg += f"\nNow it's {next_player.mention}'s turn."
                async def edit_on_death(self):
                    if self.message:
                        content = msg.split("\n")[0]
                        await self.message.edit(content=content, view=self)
                unomessage = self._build_reminder(msg, edit_on_death)
            else:
                unomessage = UnoMessage(msg)
        
        asyncio.create_task(self.update_views(UnoGameView, UnoMenuView))
        if votekicks >= threshold:
            for view in self.active_views:
                if isinstance(view, UnoHandView) and view.player == target:
                    asyncio.create_task(view.die())
        if next_player:
            asyncio.create_task(self.update_views(UnoHandView, check=lambda v: v.player == next_player))
        
        return unomessage

    def votestop(self, player):
        try:
            return_value = self.gamestate.votestop(self, player)
        except UnoException as err:
            return UnoMessage(str(err), is_ephemeral=True)

        # end game if relevant
        if not self.gamestate.in_game:
            reason = return_value
            asyncio.create_task(self.die(reason, send_message=False))
            return UnoMessage(f"{player.mention} has voted to end the game.\n{reason}")
        
        stop_added, votestops, threshold = return_value

        if not stop_added:
            msg  = f"{player.mention} has removed their vote to end the game. "
        else:
            msg  = f"{player.mention} has voted to end the game. "
            msg += f"{votestops} / {threshold} stop votes received. "
        
        return UnoMessage(msg)

    @_is_activity
    def get_hand_msg(self, player):
        # kill old hand views for this player
        for view in self.active_views:
            if isinstance(view, UnoHandView) and view.player == player:
                asyncio.create_task(view.die(delete=True))

        hand_view = UnoHandView(self.gamestate, self, player)
        self.active_views.append(hand_view)
        return UnoMessage.from_uno_view(hand_view, is_ephemeral=True)

    @_is_activity
    def draw(self, player):
        drawn_cards = self.gamestate.draw_cards(player, 1)

        if drawn_cards:
            if self.draw_notice.message:
                asyncio.create_task(self.draw_notice.die(delete=True))
            asyncio.create_task(self.update_views(UnoHandView, check=lambda v: v.player == player))
            asyncio.create_task(self.update_views(UnoGameView))
            # TODO consider making this a non-ephemeral message without the card, so people can uno better
            self.draw_notice = UnoEmptyView()
            return UnoMessage(f"You drew: {drawn_cards[0].get_name()}", self.draw_notice, is_ephemeral=True)
        return UnoMessage(f"There are no cards left in the deck! Try playing a card or passing your turn.")
    
    @_is_activity
    def uno(self, player):
        target = self.gamestate.players[self.gamestate.turn]
        valid_uno, safe = self.gamestate.uno(player, target)

        to_update = []

        if player == target:
            if valid_uno:
                msg = f"{player.mention} is safe from uno!"
            else:
                to_update.append(player)
                msg = f"{player.mention} has decided to draw a bunch of cards?"
        else:
            if not valid_uno:
                to_update.append(player)
                msg = f"{player.mention} tried to catch {target.mention}, but instead draws 4 cards."
            elif safe:
                msg = None
            else:
                to_update.append(target)
                msg = f"{player.mention} caught {target.mention}! {target.mention} draws 4 cards."

        asyncio.create_task(self.update_views(UnoHandView, check=lambda v: v.player in to_update))
        asyncio.create_task(self.update_views(UnoGameView))
        return msg


    @_is_activity
    def pass_turn(self, player):
        if self.gamestate.players[self.gamestate.turn] != player:
            # this shouldn't happen
            return UnoMessage(f"Not your turn to pass, {player.mention}!")
        self.gamestate.next_turn()

        next_player = self.gamestate.players[self.gamestate.turn]
        asyncio.create_task(self.update_views(UnoHandView, check=lambda v: v.player in [player, next_player]))
        asyncio.create_task(self.update_views(UnoGameView))

        remind_str = f"Now it's {self.gamestate.players[self.gamestate.turn].mention}'s turn!"
        return self._build_reminder(remind_str)

    @_is_activity
    def play_card(self, player, card_idx):
        # TODO handle house rules here somehow...
        hand = self.gamestate.hands[player]
        card = hand[card_idx]
        if card.is_wild() and not card.wild_color:
            wild_menu = UnoWildMenuView(self.gamestate, self, player, card_idx)
            self.active_views.append(wild_menu)
            asyncio.create_task(self.update_views(UnoHandView, check=lambda v: v.player == player))
            return UnoMessage.from_uno_view(wild_menu, is_ephemeral=True)
        else:
            try:
                victim = self.gamestate.play_card(player, card_idx)
            except UnoException as err:
                return UnoMessage(str(err), is_ephemeral=True)
        
        # handle winning
        if not self.gamestate.in_game:
            reason = victim
            asyncio.create_task(self.die(reason, send_message=False))
            return UnoMessage(reason)

        next_player = self.gamestate.players[self.gamestate.turn]
        hands_to_update = [player, next_player]

        remind_str = f"Now it's {next_player.mention}'s turn!"
        if card.is_special():
            if card.value == "skip":
                remind_str = f"{victim.mention} was skipped! {remind_str}"
            elif card.value == "reverse":
                remind_str = f"Play order has been reversed! {remind_str}"
            elif card.value == "draw 2":
                remind_str = f"Sorry, {victim.mention}! Drawing 2 and skipping you. {remind_str}"
                hands_to_update.append(victim)
            elif card.value == "draw 4":
                remind_str = f"Sorry, {victim.mention}! Drawing 4 and skipping you. {remind_str}"
                hands_to_update.append(victim)
        else:
            remind_str = f"{player.display_name} played a {card.get_name()}. {remind_str}"
        
        asyncio.create_task(self.update_views(UnoGameView))
        asyncio.create_task(self.update_views(UnoHandView, check=lambda v: v.player in hands_to_update))

        return self._build_reminder(remind_str)
    
    async def die(self, reason=None, send_message=True, timed_out=False):
        await asyncio.gather(*(view.die(reason) for view in self.active_views))

        if not timed_out:
            self._timeout_check.cancel()

        if send_message:
            await self.parent_cog.cleanup_game(self.channel_id, reason)
        else:
            await self.parent_cog.cleanup_game(self.channel_id)
        return reason

    async def _check_timeout(self):
        max_idle_time = 300 # die after five minutes of no activity
        post_activity_sleep = 30
        is_active = False
        try:
            while await asyncio.wait_for(self._activity_flag.wait(), max_idle_time - (post_activity_sleep * is_active)):
                self._activity_flag.clear()

                # don't waste too much time flipping the flag
                is_active = True
                await asyncio.sleep(post_activity_sleep)
        except TimeoutError:
            await self.die("The game has ended: Timed out.", timed_out=True)
        except asyncio.CancelledError:
            pass
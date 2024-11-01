import discord

from lib.uno.models import UnoException

import asyncio

# TODO handle non-players touching buttons

class UnoView(discord.ui.View):
    """ Generic View for use in Uno
    
    Automatically removes self from list of active views in controller on death. Watch out!"""
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)
        self.controller = None
        self.content = None
        self.message = None

    async def die(self, reason=None, *, delete=False):
        for item in self.children:
            item.disabled = True

        msg = self.message
        if msg:
            if delete:
                await msg.delete()
            else:
                content = f"~~{self.content}~~\n" if self.content else ""
                reason  = f": {reason}"           if reason       else "."

                content += f"This interaction has been disabled{reason}"
                await msg.edit(content=content, view=self)

        if self.controller:
            self.controller.active_views.remove(self)

        self.stop()

        if msg is None:
            raise UnoException("Could not find message for UnoView before dying!")

    def update_contents(self):
        raise NotImplementedError("Tried updating an unimplemented UnoView!")

    async def update(self):
        self.update_contents()
        if self.message:
            await self.message.edit(content=self.content, view=self)

class UnoEmptyView(UnoView):
    def __init__(self, on_death=None):
        super().__init__()
        self.on_death = on_death
    
    async def die(self, reason=None, *, delete=False):
        # TODO why is delete a keyword here
        if self.message:
            if self.on_death:
                self.on_death(self)
            else:
                await self.message.delete()
                self.message = None
        else:
            raise UnoException("Could not find message for Reminder before dying!")

class UnoLobbyView(UnoView):
    def __init__(self, gamestate, controller):
        super().__init__()
        self.gamestate  = gamestate
        self.controller = controller

        self.update_contents()

    @discord.ui.button(label='Join')
    async def join_button(self, interaction, button):
        message = self.controller.join(interaction.user)
        print("joined game, responding:")
        await message.respond_to(interaction)
        print("responded")

    @discord.ui.button(label='Leave', style=discord.ButtonStyle.danger)
    async def leave_button(self, interaction, button):
        message = self.controller.leave(interaction.user)
        if message:
            await message.respond_to(interaction)
        else:
            await interaction.response.pong()

    @discord.ui.button(label='Start game', disabled=True, style=discord.ButtonStyle.primary, row=1)
    async def start_button(self, interaction, button):
        message = self.controller.start_game(interaction.user)
        await message.respond_to(interaction)

    def update_contents(self):
        num_players = len(self.gamestate.players)
        self.content = f"An uno lobby is now open! Press 'join' to join!\n{num_players} player{'' if num_players == 1 else 's'} currently in lobby."

        start_button, = [button for button in self.children if button.label == 'Start game']
        if num_players > 1:
            start_button.disabled = False
        else:
            start_button.disabled = True

class UnoGameView(UnoView):
    def __init__(self, gamestate, controller):
        super().__init__()
        self.gamestate  = gamestate
        self.controller = controller

        self.update_contents()

    @discord.ui.button(label='View hand', style=discord.ButtonStyle.primary)
    async def hand_button(self, interaction, button):
        message = self.controller.get_hand_msg(interaction.user)
        await message.respond_to(interaction)

    @discord.ui.button(label='View game menu', row=1)
    async def menu_button(self, interaction, button):
        message = self.controller.get_menu_msg(interaction.user)
        await message.respond_to(interaction)

    @discord.ui.button(label='Leave game', style=discord.ButtonStyle.danger, row=1)
    async def leave_button(self, interaction, button):
        message = self.controller.leave(interaction.user)
        await message.respond_to(interaction)

    def update_contents(self):
        players = self.gamestate.players
        turn    = self.gamestate.turn
        topcard = self.gamestate.discard[-1]

        turn_order = players[turn:] + players[:turn]
        if self.gamestate.direction == -1:
            turn_order.reverse()
            turn = len(players) - turn - 1

        self.content  = f"It's {players[turn].mention}'s turn! Turn order is:\n"
        self.content += f"{" > ".join(player.display_name for player in turn_order)}\n\n"

        uno_warning = ""
        THRESHOLD = 3
        for player in players:
            if len(self.gamestate.hands[player]) <= THRESHOLD:
                self.content += f"{player.mention} has {THRESHOLD} or fewer cards!\n"

        if uno_warning:
            self.content += uno_warning + "\n"

        self.content += f"Last played card is: {topcard.get_name()}"
        # TODO handle image

    async def update(self):
        await asyncio.sleep(0)
        self.update_contents()
        if self.message:
            # TODO overload to handle image
             await self.message.edit(content=self.content, view=self)

class UnoHandView(UnoView):
    def __init__(self, gamestate, controller, player):
        super().__init__()
        self.gamestate  = gamestate
        self.controller = controller

        self.player     = player
        self.disabled   = False

        # keep buttons and selectors organized here:
        # TODO see if these are actually necessary; I think the decorator makes the functions the actual objects
        #self.card_selector, = [button for button in self.children if isinstance(button, discord.ui.Select)]

        #self.pass_element, = [button for button in self.children if isinstance(button, discord.ui.Button) and button.label == "Pass"]
        #self.draw_element, = [button for button in self.children if isinstance(button, discord.ui.Button) and button.label == "Draw"]

        self.page_buttons = [button for button in self.children if isinstance(button, discord.ui.Button) and "View" in button.label]
        self.page_number  = 0

        self.update_contents()

    @discord.ui.select(cls=discord.ui.Select, placeholder='Select a card to play!', row=0)
    async def card_select(self, interaction, select):
        card_idx = int(select.values[0])

        message = self.controller.play_card(self.player, card_idx)
        if message:
            await message.respond_to(interaction)
        else:
            await interaction.response.pong()

    @discord.ui.button(label='View previous cards', row=1)
    async def prev_button(self, interaction, button):
        if self.page_number <= 0:
            return await interaction.response.send_message("You're already viewing the first page of cards!", ephemeral=True)
        self.page_number -= 1
        await self.update()
        await interaction.response.pong()

    @discord.ui.button(label='View next cards', row=1)
    async def next_button(self, interaction, button):
        if (self.page_number + 1) * 25 >= len(self.gamestate.hands[self.player]):
            return await interaction.response.send_message("You're already viewing the last page of cards!", ephemeral=True)
        self.page_number += 1
        await self.update()
        await interaction.response.pong()

    @discord.ui.button(label='Draw', row=2)
    async def draw_button(self, interaction, button):
        message = self.controller.draw(interaction.user)
        await message.respond_to(interaction)

    @discord.ui.button(label='Pass', row=2)
    async def pass_button(self, interaction, button):
        message = self.controller.pass_turn(interaction.user)
        await message.respond_to(interaction)

    def update_contents(self):
        is_current_player = self.gamestate.players[self.gamestate.turn] == self.player

        # always display cards
        if is_current_player:
            self.content = f"Top of the discard pile is: {self.gamestate.discard[-1].get_name()}\n"
        else:
            self.content = f"It's not your turn right now!\n\n"
        self.content += f"Your hand is:\n"

        card_options = []
        for idx, card in enumerate(self.gamestate.hands[self.player]):
            self.content += f"**{idx+1}**: {card.get_name()}\n"
            card_options.append(discord.SelectOption(label=f"{idx+1}. {card.get_name(True)}", value=idx))

        # enable/disable elements as appropriate
        if not is_current_player or self.disabled:
            for element in self.children:
                if not isinstance(element, discord.ui.Button) or element.label != "View menu":
                    element.disabled = True
                    if isinstance(element, discord.ui.Select):
                        element.options = [discord.SelectOption(label="Not your turn!")] # need at least one placeholder option
            return

        # handle interactive elements only if current turn
        for element in self.children:
            element.disabled = False

        # pagination over 25 cards to prevent selects from breaking
        SELECT_MAX = 25
        if len(card_options) > SELECT_MAX:
            lower = SELECT_MAX * self.page_number
            length = min(SELECT_MAX, len(card_options) - lower)
            card_options = card_options[lower : lower + length]

            for button in self.page_buttons:
                if button not in self.children:
                    self.add_item(button)

            prev, next = self.page_buttons
            prev.disabled = self.page_number == 0
            next.disabled = (self.page_number + 1) * 25 >= len(self.gamestate.hands[self.player])
        else:
            for button in self.page_buttons:
                if button in self.children:
                    self.remove_item(button)
        self.card_select.options = card_options

        # add/remove pass button when no cards are left in deck
        if self.gamestate.deck_empty():
            self.draw_button.disabled = True
            if self.pass_button not in self.children:
                self.add_item(self.pass_button)
        else:
            self.draw_button.disabled = False
            if self.pass_button in self.children:
                self.remove_item(self.pass_button)

class UnoWildMenuView(UnoView):
    """ Menu to select color of a played wild card
    
    Implicitly disables player hand buttons while alive. Watch out! """

    def __init__(self, gamestate, controller, player, card_idx):
        super().__init__()
        self.gamestate  = gamestate
        self.controller = controller

        self.player = player
        self.card_idx = card_idx

        self.card = self.gamestate.hands[player][card_idx]

        hand_view = self.get_hand_view()
        if hand_view:
            hand_view.disabled = True
        self.update_contents()
    
    def get_hand_view(self):
        for view in self.controller.active_views:
            if isinstance(view, UnoHandView) and view.player == self.player:
                return view
        return None

    def play_colored(self, color):
        self.card.set_wild_color(color)
        return self.controller.play_card(self.player, self.card_idx)

    @discord.ui.button(label='Red', row=0)
    async def red_button(self, interaction, button):
        message = self.play_colored("red")
        if message:
            await message.respond_to(interaction)
        else:
            await interaction.response.pong()
        await self.die()

    @discord.ui.button(label='Yellow', row=0)
    async def yellow_button(self, interaction, button):
        message = self.play_colored("yellow")
        if message:
            await message.respond_to(interaction)
        else:
            await interaction.response.pong()
        await self.die()

    @discord.ui.button(label='Green', row=0)
    async def green_button(self, interaction, button):
        message = self.play_colored("green")
        if message:
            await message.respond_to(interaction)
        else:
            await interaction.response.pong()
        await self.die()

    @discord.ui.button(label='Blue', row=0)
    async def blue_button(self, interaction, button):
        message = self.play_colored("blue")
        if message:
            await message.respond_to(interaction)
        else:
            await interaction.response.pong()
        await self.die()

    @discord.ui.button(label='Cancel', row=1)
    async def cancel_button(self, interaction, button):
        await interaction.response.pong()
        await self.die() # also removes self from controller

    async def die(self, reason=None):
        await super().die(reason, delete=True)

        hand_view = self.get_hand_view()
        if hand_view:
            hand_view.disabled = False
            await hand_view.update()

    def update_contents(self):
        self.content  = f"Choose a color for your {self.card.get_name()}:"

class UnoMenuView(UnoView):
    def __init__(self, gamestate, controller, player):
        super().__init__()
        self.gamestate  = gamestate
        self.controller = controller
        self.player     = player

        self.update_contents()

    @discord.ui.select(cls=discord.ui.Select, placeholder='Votekick players')
    async def votekick_select(self, interaction, select):
        target = self.gamestate.players[int(select.values[0])]
        message = self.controller.votekick(interaction.user, target)
        await message.respond_to(interaction)

    @discord.ui.button(label='Votestop the game')
    async def votestop_button(self, interaction, button):
        message = self.controller.votestop(interaction.user)
        await message.respond_to(interaction)

    @discord.ui.button(label='Leave game', style=discord.ButtonStyle.danger)
    async def leave_button(self, interaction, button):
        message = self.controller.leave(interaction.user)
        await message.respond_to(interaction)

    def update_user_select(self):
        if len(self.votekick_select.options) == len(self.gamestate.players) - 1:
            return

        # pagination never -- 25+ player game of uno sounds horrible
        votekick_options = []
        for idx, target in enumerate(self.gamestate.players):
            # don't votekick yourself
            if target == self.player:
                continue
            label = f"{['K', 'Unk'][self.player in self.gamestate.kicks[target]]}ick {target.display_name}"
            votekick_options.append(discord.SelectOption(label=label, value=idx))
        self.votekick_select.options = votekick_options

    def update_contents(self):
        self.content  = f"Choose a menu option:"
        self.update_user_select()

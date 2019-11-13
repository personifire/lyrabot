import discord
from discord.ext import commands

import asyncio
import random

"""
Uno!

Has a deck, a discard pile, and hands for every player.
Players are PM'd their hands after every change -- that is, draws and plays.

Players join the lobby individually, and can leave at any time. 
    Players are kicked from the lobby after ten minutes without starting the game.
    Needs at least 2 players to play.
    Anybody in the lobby can start the game immediately.

ideas:
    ability to play cards through PM
    house rules

"""

DEAL_SIZE = 7

class uno(commands.Cog):
    def __init__(self, client):
        self.lock       = asyncio.Lock()
        self.debug      = False
        self.call_level = 0
        self.reset_state()

    async def help(self, ctx):
        await self.debug_print("help entered", ctx)
        self.call_level += 1
        # remember to update uno() for new commands
        helpstr  = "```"
        helpstr += "!uno [help]             Prints this message\n"
        helpstr += "!uno join               Joins the lobby\n"
        helpstr += "!uno leave              Leaves the lobby or the game\n"
        helpstr += "!uno start              Starts a game with everybody in the lobby\n"
        helpstr += "!uno stop               Votes to end the game early\n"
        helpstr += "!uno kick <mention>     Tries to votekick mentioned player\n"
        helpstr += "!uno play <num>         Plays a card from your hand\n"
        helpstr += "!uno draw [num]         Draws cards from the deck\n"
        helpstr += "!uno hand               Tells you what cards are in your hand\n"
        helpstr += "```"
        await ctx.channel.send(helpstr)

        self.call_level -= 1

    async def join(self, ctx):
        await self.debug_print("join entered...", ctx)
        self.call_level += 1

        if not self.in_game:
            if ctx.author in self.players:
                await ctx.channel.send("You can't join a game twice :V")
                return
            await self.debug_print("... attempting to add player", ctx)
            self.players.append(ctx.author)
            num_players = len(self.players)
            if num_players <= 1:
                await ctx.channel.send(ctx.author.name + ' has started an Uno lobby! Type "!uno join" to join.')
            else:
                await ctx.channel.send(ctx.author.name + " has joined the game! Total players: " + str(num_players))
            await self.debug_print("... player list: " + str(list(map(lambda p: p.name, self.players))), ctx)
        else:
            await ctx.channel.send("Sorry, " + ctx.author.name + ", wait for the current game to end before joining.")
            await self.debug_print("... player list: " + str(list(map(lambda p: p.name, self.players))), ctx)
        self.call_level -= 1

    async def leave(self, ctx):
        await self.debug_print("leave entered...", ctx)
        self.call_level += 1

        player = ctx.author
        if player not in self.players:
            await ctx.channel.send("You can't leave if you haven't joined!")
            await self.debug_print("... player list: " + str(list(map(lambda p: p.name, self.players))), ctx)
            return

        await self.debug_print("... attempting to remove player", ctx)
        self.remove_player(player)

        await ctx.channel.send(player.name + " has left the game. " + str(len(self.players)) + " players remain.")
        await self.debug_print("... player list: " + str(list(map(lambda p: p.name, self.players))), ctx)

        if len(self.players) <= 1:
            await self.debug_print("... attempting to end game", ctx)
            self.end_game()
            await ctx.channel.send("Too few players left. Game's gonna have to end early!")
            await self.debug_print("... in-game status: " + str(self.in_game), ctx)
        self.call_level -= 1

    async def start(self, ctx):
        await self.debug_print("start entered...", ctx)
        self.call_level += 1

        if self.in_game:
            await ctx.channel.send("Can't start a game already in progress.")
            return
        if len(self.players) < 2:
            await ctx.channel.send("Not enough players. Get at least two to play!")
            return
        elif ctx.author not in self.players:
            await ctx.channel.send("Let's wait for one of the players to start, yes?")
            return

        await self.debug_print("... dealing cards", ctx)
        random.shuffle(self.deck)

        for player in self.players:
            self.hands[player] = self.deck[-DEAL_SIZE:]
            del self.deck[-DEAL_SIZE:]

        await self.debug_print("... starting discard pile", ctx)
        while len(self.discard) < 1 or self.discard[-1][0] == "wild":
            if len(self.discard) != 0:
                await ctx.channel.send("Whoops! Let's try that again...")
            card = self.deck.pop()
            self.discard.append(card)
            await ctx.channel.send("Putting the top card on the discard! " + self.card_name(card))

        await self.debug_print("... starting game", ctx)
        self.in_game   = True
        self.top_color = self.discard[-1][0]

        msg = "Game is starting! Turn order: "
        for player in self.players:
            msg += "<@" + str(player.id) + "> "
        await ctx.channel.send(msg)
        self.turn -= self.direction # compensate for preincrement in new turn
        await self.new_turn(ctx)

        self.call_level -= 1

    async def stop(self, ctx):
        await self.debug_print("stop entered...", ctx)
        self.call_level += 1

        if not self.in_game:
            await ctx.channel.send("You can't stop a game that isn't going, silly!")
            return
        if ctx.author not in self.players:
            await ctx.channel.send("Let's give the players the choice of when to end, yes?")
            return

        votestop_threshold = 1 + (len(self.players) // 2)
        if ctx.author in self.stops:
            await ctx.channel.send('You can only vote to end the game once! Try "!uno leave" to leave early.')
        else:
            await self.debug_print("... adding new stop vote", ctx)
            self.stops.add(ctx.author)

            await ctx.channel.send(ctx.author.name + " has voted to end the game. " + 
                    str(len(self.stops)) + "/" + str(votestop_threshold) + " stop votes received.")
            await self.debug_print("... stop votes: " + str(list(map(lambda p: p.name, self.stops))), ctx)

            if len(self.stops) >= votestop_threshold:
                await self.debug_print("... stopping game", ctx)
                self.end_game()
                await ctx.channel.send("Stop votes received! Game is ending.")
        self.call_level -= 1

    async def kick(self, ctx, *args):
        await self.debug_print("kick entered...", ctx)
        self.call_level += 1

        if not self.in_game:
            await ctx.channel.send("You should probably wait until the game is started to start kicking people.")
            return
        if ctx.author not in self.players:
            await ctx.channel.send("Let's leave the kicking to the people in the game, yes?")
            return

        votekick_threshold = 1 + (len(self.players) // 3)
        if ctx.message.mentions:
            for player in ctx.message.mentions:
                if player not in self.kicks:
                    await self.debug_print("... adding new kick vote", ctx)
                    self.kicks[player] = {ctx.author}
                else:
                    if ctx.author in self.kicks[player]:
                        await ctx.channel.send("You can only vote to kick someone once!")
                        return
                    else:
                        await self.debug_print("... adding new kick vote", ctx)
                        self.kicks[player].add(ctx.author)

                await ctx.channel.send(ctx.author.name + " has voted to kick " + player.name + ". " +
                        str(len(self.kicks[player])) + "/" + str(votekick_threshold) + " kick votes received.")

                await self.debug_print("... kick votes: " + str(list(map(lambda p: p.name, self.kicks[player]))), ctx)

                if len(self.kicks[player]) >= votekick_threshold:
                    await ctx.channel.send("Removing " + player.name + " from the game now. Sorry, bud!")
                    await self.debug_print("... removing player " + player.name, ctx)
                    self.remove_player(player)
                    self.turn -= self.direction
                    self.new_turn(ctx)
        if len(self.players) <= 1:
            await self.debug_print("... attempting to end game", ctx)
            self.end_game()
            await ctx.channel.send("Too few players left. Game's gonna have to end early!")
            await self.debug_print("... in-game status: " + str(self.in_game), ctx)
        self.call_level -= 1

    async def play(self, ctx, *args):
        await self.debug_print("play entered...", ctx)
        self.call_level += 1
        player = ctx.author

        if not self.in_game:
            await ctx.channel.send("Wait for the game to start before trying to play your cards!")
        elif player != self.players[self.turn]:
            await ctx.channel.send("Wait for your turn, " + player.name + "!")
        elif not args:
            await ctx.channel.send("You need to select a card to play.")
        else:
            try:
                index = int(args[0])
            except ValueError:
                await ctx.channel.send("Try a number, instead.")
                return
            if index <= 0 or index > len(self.hands[player]):
                await ctx.channel.send("Try a number that makes sense, instead.")
                return

            card = self.hands[player][index - 1]
            top  = self.discard[-1]
            colors   = ["red", "yellow", "green", "blue"]
            if card[0] == "wild":
                if len(args) < 2 or args[1].lower() not in colors:
                    await ctx.channel.send('You need to provide a color! Like so: "!uno play ' + args[0] + ' red"')
                    return
                else:
                    wildcolor = args[1].lower()
            elif card[0] != self.top_color and card[1] != top[1]:
                await ctx.channel.send("You can't put a " + self.card_name(card) + " on that " + self.card_name(top) + "!")
                return

            await self.debug_print("... hand before playing: " + str(self.hands[player]), ctx)
            await self.debug_print("... playing card " + str(index), ctx)

            self.discard.append(self.hands[player].pop(index - 1))
            self.top_color = self.discard[-1][0]
            if card[0] == "wild":
                self.top_color = wildcolor
            if card[1] == "skip":
                self.turn += self.direction
            elif card[1] == "reverse":
                self.direction = -self.direction
            elif card[1] == "draw 2":
                self.turn += self.direction
                receiver = self.players[self.turn % len(self.players)]
                await receiver.send(self.give_cards(receiver, 2))
            elif card[1] == "draw 4":
                self.turn += self.direction
                receiver = self.players[self.turn % len(self.players)]
                await receiver.send(self.give_cards(receiver, 4))

            await self.debug_print("... hand after playing: " + str(self.hands[player]), ctx)
            await self.debug_print("... discard after playing: " + str(self.discard), ctx)

            if len(self.hands[player]) == 0:
                await ctx.channel.send("<@" + str(player.id) + "> Wins! Congrats. The game is now over!")
                await self.debug_print("... ending game", ctx)
                self.end_game()
                return

            await self.new_turn(ctx)
        self.call_level -= 1

    async def draw(self, ctx, *args):
        await self.debug_print("draw entered...", ctx)
        self.call_level += 1
        player = ctx.author

        if not self.in_game:
            await ctx.channel.send("Wait for the game to start before drawing!")
        elif player != self.players[self.turn]:
            await ctx.channel.send("Wait for your turn, " + player.name + "!")
        else:
            await self.debug_print("... trying to find number of cards to draw", ctx)
            num_cards = 1
            if len(args) > 0:
                await self.debug_print("... trying to parse args", ctx)
                try:
                    num_cards = int(args[0])
                except ValueError:
                    await ctx.channel.send("You can't draw that, try a number instead.")
                    return
                if num_cards < 0 or num_cards > 10:
                    await ctx.channel.send("Try a more reasonable number, instead.")
                    return

            await self.debug_print("... trying to draw " + str(num_cards) + " card(s)", ctx)

            if len(self.deck) == 0:
                await ctx.channel.send("Not enough cards left in the deck to draw. Passing turn...")
                await self.debug_print("... passing turn", ctx)
                self.new_turn(ctx)

            await self.debug_print("... drawing card(s)", ctx)
            msg = self.give_cards(player, num_cards)

            await player.send(msg)
        self.call_level -= 1

    async def hand(self, ctx):
        await self.debug_print("hand entered...", ctx)
        self.call_level += 1

        if not self.in_game:
            await ctx.channel.send("Wait for the game to start before looking at your hand!")
            return
        elif ctx.author not in self.players:
            await ctx.channel.send("You can't look at your hand if you're not in the game!")
            return
        await self.send_hand(ctx.author)
        await ctx.channel.send("Your hand has been sent, " + ctx.author.name + ". Check your messages!")

        self.call_level -= 1

    async def debug(self, ctx):
        await self.debug_print("debug entered...", ctx)
        self.debug = not self.debug

    @commands.command(pass_context = True)
    async def uno(self, ctx, *args):
        await self.lock.acquire()
        try:
            if args:
                # remember to update help() for new commands
                if   args[0] == "help":
                    await self.help(ctx)
                elif args[0] == "join":
                    await self.join(ctx)
                elif args[0] == "leave":
                    await self.leave(ctx)
                elif args[0] == "start":
                    await self.start(ctx)
                elif args[0] == "stop":
                    await self.stop(ctx)
                elif args[0] == "kick":
                    await self.kick(ctx, *args[1:])
                elif args[0] == "play":
                    await self.play(ctx, *args[1:])
                elif args[0] == "draw":
                    await self.draw(ctx, *args[1:])
                elif args[0] == "hand":
                    await self.hand(ctx)
                elif args[0] == "debug":
                    await self.debug(ctx)
                else:
                    await ctx.channel.send("Unknown uno command '" + args[0] + '. Try "!uno help"')
            else:
                await self.help(ctx)
            self.call_level = 0
            await self.debug_print("end command", ctx)
        finally:
            self.lock.release()

###################################################################################################

    async def debug_print(self, string, ctx = None):
        if ctx is not None:
            self.channel = ctx.channel
        string = "  " * self.call_level + string

        print(string)
        if self.debug:
            if self.channel is None:
                raise ValueError("Did not have context available to send message to")
            else:
                await self.channel.send(string)

    def card_name(self, card):
        color_emojis = { "red": "heart", 
                         "yellow": "yellow_heart", 
                         "green" : "green_heart", 
                         "blue"  : "blue_heart", 
                         "wild"  : "gay_pride_flag" }
        value_emojis = { "0"      : "zero",
                         "1"      : "one",
                         "2"      : "two",
                         "3"      : "three",
                         "4"      : "four",
                         "5"      : "five",
                         "6"      : "six",
                         "7"      : "seven",
                         "8"      : "eight",
                         "9"      : "nine",
                         "skip"   : "no_entry_sign",
                         "reverse": "cyclone",
                         "draw 2" : "bangbang",
                         ""       : "gay_pride_flag",
                         "draw 4" : "bangbang: :bangbang" }

        if card[0] == "wild" and card[1] == "":
            name = ":" + color_emojis[card[0]] + ": :" + value_emojis[card[1]] + ": " + card[0]
        else:
            name = ":" + color_emojis[card[0]] + ": :" + value_emojis[card[1]] + ": " + card[0] + " " + card[1]
        return name

    async def send_hand(self, player):
        self.call_level += 1
        await self.debug_print("... sending hand")
        await self.debug_print("... hand is: " + str(self.hands[player]))

        hand = player.name + " , your current uno hand is:\n"
        await self.debug_print("... building message")
        for idx, card in enumerate(self.hands[player]):
            await self.debug_print("... adding card to message")
            hand += "**" + str(idx + 1) + "**: "
            hand += self.card_name(card) + "\n"

        await self.debug_print("... sending message")
        await player.send(hand)
        top_msg = "Top of the discard pile is: " + self.card_name(self.discard[-1])
        if self.discard[-1][0] == "wild":
            top_msg += " (" + self.top_color + ")"
        await player.send(top_msg)

        self.call_level -= 1

    async def new_turn(self, ctx):
        self.call_level += 1
        await self.debug_print("... starting new turn", ctx)
        await self.debug_print("... previous turn counter is: " + str(self.turn), ctx)
        await self.debug_print("... turn direction is: " + str(self.direction), ctx)
        await self.debug_print("... players are: " + str(list(map(lambda p: p.name, self.players))), ctx)
        self.turn = (self.turn + self.direction) % len(self.players)

        await self.debug_print("... active player is: " + self.players[self.turn].name, ctx)
        await self.send_hand(self.players[self.turn])
        await ctx.channel.send("<@" + str(self.players[self.turn].id) + ">, it's your turn!")
        top_msg = "Top of the discard pile is: " + self.card_name(self.discard[-1])
        if self.discard[-1][0] == "wild":
            top_msg += " (" + self.top_color + ")"
        await ctx.channel.send(top_msg)

        self.call_level -= 1

    def give_cards(self, player, num_cards):
        msg = "You drew:\n"
        cards = []
        for card in range(num_cards):
            if len(self.deck) == 0:
                self.reshuffle()
            card = self.deck.pop()
            self.hands[player].append(card)
            cards.append(card)
            msg += "**" + str(len(self.hands[player])) + "**: " + self.card_name(card) + "\n"
        return msg

    def reshuffle(self):
        topcard = self.discard.pop()
        random.shuffle(discard)
        self.deck = self.discard + self.deck
        self.discard = [topcard]

    def end_game(self):
        for player in self.players:
            self.remove_player(player)
        self.reset_state()

    def remove_player(self, player):
        if self.in_game:
            self.discard = self.hands[player] + self.discard
            del self.hands[player]

            if player in self.kicks:
                del self.kicks[player]
            for votekick in self.kicks:
                if player in votekick:
                    self.kicks[votekick].remove(player)
            if player in self.stops:
                self.stops.remove(player)

            self.players.remove(player)
        else:
            self.players.remove(player)

    def reset_state(self):
        self.in_game = False
        self.deck    = []
        self.discard = []
        self.players = []
        self.hands   = {}
        self.kicks   = {}
        self.stops   = set()
        self.turn    = 0

        self.top_color = ""
        self.direction = 1

        colors   = ["red", "yellow", "green", "blue"]
        numbers  = [0] + list(range(1, 10)) * 2
        specials = ["skip", "reverse", "draw 2"] * 2
        wilds    = ["", "draw 4"] * 4

        self.deck += [(color, str(number)) for color in colors for number in numbers]
        self.deck += [(color, special)     for color in colors for special in specials]
        self.deck += [("wild", wildtype)   for wildtype in wilds]

def setup(client):
    client.add_cog(uno(client))

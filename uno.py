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
    house rules?
    emoji card display -- :heart: :yellow_heart: :green_heart: :blue_heart:, :zero: :one: ... :nine:

"""

DEAL_SIZE = 7

class uno:
    def __init__(self, client):
        self.client = client
        self.lock   = asyncio.Lock()
        self.reset_state()

    async def help(self):
        # remember to update uno() for new commands
        helpstr  = "```"
        helpstr += "!uno [help]             Prints this message\n"
        helpstr += "!uno join               Joins the lobby\n"
        helpstr += "!uno leave              Leaves the lobby or the game\n"
        helpstr += "!uno start              Starts a game with everybody in the lobby\n"
        #helpstr += "!uno stop               Votes to end the game early\n"
        #helpstr += "!uno kick <mention>     Tries to votekick mentioned player\n"
        #helpstr += "!uno play <card | num>  Plays a card from your hand\n"
        helpstr += "!uno play <num>         Plays a card from your hand\n"
        helpstr += "!uno draw               Draws a card from the deck\n"
        helpstr += "!uno hand               Tells you what cards are in your hand\n"
        helpstr += "```"
        await self.client.say(helpstr)

    async def join(self, ctx):
        if not self.in_game:
            await self.lock.acquire()
            try:
                if ctx.message.author in self.players:
                    await self.client.say("You can't join a game twice :V")
                    return
                else:
                    self.players.append(ctx.message.author)
            finally:
                self.lock.release()
            num_players = len(self.players)
            if num_players <= 1:
                await self.client.say(ctx.message.author.name + ' has started an Uno lobby! Type "!uno join" to join.')
            else:
                await self.client.say(ctx.message.author.name + " has joined the game! Total players: " + str(num_players))
        else:
            await self.client.say("Sorry, " + ctx.message.author.name + ", wait for the current game to end before joining.")

    async def leave(self, ctx):
        player = ctx.message.author
        if player not in self.players:
            await self.client.say("You can't leave if you haven't joined!")
            return

        await self.lock.acquire()
        try:
            self.remove_player(player)
        finally:
            self.lock.release()

        await self.client.say(player.name + " has left the game. " + str(len(self.players)) + " players remain.")

        if len(self.players) <= 1:
            await self.lock.acquire()
            try:
                self.end_game()
            finally:
                self.lock.release()
            await self.client.say("Too few players left. Ending the game now, sorry!")

    async def start(self, ctx):
        if len(self.players) < 2:
            await self.client.say("Not enough players. Get at least two to play!")
            return
        await self.lock.acquire()
        try:
            random.shuffle(self.deck)

            for player in self.players:
                self.hands[player] = self.deck[-DEAL_SIZE:]
                del self.deck[-DEAL_SIZE:]
            self.discard.append(self.deck.pop())

            self.in_game = True
        finally:
            self.lock.release()
        msg = "Game is starting! Turn order: "
        for player in self.players:
            msg += "<@" + player.id + "> "
        await self.client.say(msg)
        await self.lock.acquire()
        try:
            self.turn -= self.direction # compensate for preincrement in new turn
            await self.new_turn()
        finally:
            self.lock.release()

    async def stop(self, ctx):
        if not self.in_game:
            await self.client.say("You can't stop a game that isn't going, silly!")
            return

        votestop_threshold = 1 + (len(self.players) // 2)
        if ctx.message.author in self.stops:
            await self.client.say('You can only vote to end the game once! Try "!uno leave" to leave early.')
        else:
            await self.lock.acquire()
            try:
                self.stops.add(ctx.message.author)
            finally:
                self.lock.release()
            await self.client.say(ctx.message.author.name + " has voted to end the game. " + 
                                  str(len(self.stops)) + "/" + str(votestop_threshold) + " stop votes received.")

        if len(self.stops) > len(self.players) // 3:
            await self.lock.acquire()
            try:
                self.end_game()
            finally:
                self.lock.release()
            await self.client.say("Stop votes received! Game is ending.")

    async def kick(self, ctx, *args):
        if not self.in_game:
            await self.client.say("You can wait until the game is started to start kicking people.")
            return

        votekick_threshold = 1 + (len(self.players) // 3)
        if ctx.message.mentions:
            player = ctx.message.mentions[0]
            await self.lock.acquire()
            try:
                if player not in self.kicks:
                    self.kicks[player] = {ctx.message.author}
                else:
                    if ctx.message.author in self.kicks[player]:
                        await self.client.say("You can only vote to kick someone once!")
                    else:
                        self.kicks[player].add(ctx.message.author)
            finally:
                self.lock.release()
            await self.client.say(ctx.message.author.name + " has voted to kick " + player.name + ". " +
                                  str(len(self.kicks[player])) + "/" + str(votekick_threshold) + " kick votes received.")

    async def play(self, ctx, *args):
        player = ctx.message.author
        if not self.in_game:
            await self.client.say("Wait for the game to start before trying to play your cards!")
        elif player != self.players[self.turn]:
            await self.client.say("Wait for your turn, " + player.name + "!")
        elif not args:
            await self.client.say("You need to select a card to play.")
        else:
            try:
                index = int(args[0])
            except ValueError:
                await self.client.say("Try a number, instead.")
                return
            if index < 0 or index > len(self.hands[player]):
                await self.client.say("Try a number that makes sense, instead.")
                return

            card = self.hands[player][index - 1]
            top  = self.discard[-1]
            if card[0] != top[0] and card[1] != top[1]:
                await self.client.say("You can't put that card there!")
                return
            await self.lock.acquire()
            try:
                if card[0] == "wild":
                    pass # TODO figure out how wildcards work
                elif card[1] == "skip":
                    self.turn += self.direction
                elif card[1] == "reverse":
                    self.direction = -self.direction
                elif card[1] == "draw 2":
                    self.turn += self.direction
                    receiver = self.players[self.turn % len(self.players)]
                    await self.client.send_message(receiver, self.give_cards(receiver, 2))
                self.discard.append(self.hands[player].pop(index - 1))
                await self.new_turn()
            finally:
                self.lock.release()

    async def draw(self, ctx, *args):
        player = ctx.message.author
        if not self.in_game:
            await self.client.say("Wait for the game to start before drawing!")
        elif player != self.players[self.turn]:
            await self.client.say("Wait for your turn, " + player.name + "!")
        else:
            num_cards = 1
            if args:
                try:
                    num_cards = int(args[0])
                except ValueError:
                    await self.client.say("You can't draw that, try a number instead.")
                    return
                if num_cards < 0 or num_cards > 10:
                    await self.client.say("Try a more reasonable number, instead.")
                    return
            await self.lock.acquire()
            try:
                msg = self.give_cards(player, num_cards)
            finally:
                self.lock.release()
            await self.client.send_message(player, msg)

    async def hand(self, ctx):
        await self.send_hand(ctx.message.author)

    @commands.command(pass_context = True)
    async def uno(self, ctx, *args):
        if args:
            # remember to update help() for new commands
            if   args[0] == "help":
                await self.help()
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
            else:
                await self.client.say("Unknown uno command" + args[0] + '. Try "!uno help"')
            return
        else:
            await self.help()

###################################################################################################

    def card_name(self, card):
        color_emojis = { "red"   : "heart", 
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
                         "draw 2" : "exclamation",
                         "draw 4" : "bangbang" }

        name = ":" + color_emojis[card[0]] + ": :" + value_emojis[card[1]] + ": " + card[0] + " " + card[1]
        return name

    async def send_hand(self, player):
        hand = player.name + " , your current uno hand is:\n"
        for idx, card in enumerate(self.hands[player]):
            hand += "**" + str(idx + 1) + "**: "
            hand += self.card_name(card) + "\n"
        await self.client.send_message(player, hand)
        await self.client.send_message(player, "Top of the discard pile is: " + self.card_name(self.discard[-1]))

    async def new_turn(self):
        if not self.lock.locked():
            print("Not locked -- won't do anything in case of concurrent issues.")
            return
        self.turn = (self.turn + self.direction) % len(self.players)
        await self.send_hand(self.players[self.turn])
        await self.client.say("<@" + self.players[self.turn].id + ">, it's your turn!")
        await self.client.say("Top of the discard pile is: " + self.card_name(self.discard[-1]))

    def give_cards(self, player, num_cards):
        if not self.lock.locked():
            print("Not locked -- won't do anything in case of concurrent issues.")
            return
        msg = "You drew:\n"
        cards = []
        for card in range(num_cards):
            if len(self.deck) == 0:
                self.reshuffle()
            card = self.deck.pop()
            self.hands[player].append(card)
            cards.append(card)
            msg += "*" + str(len(self.hands[player])) + "*: " + self.card_name(card) + "\n"
        return msg

    def reshuffle(self):
        if not self.lock.locked():
            print("Not locked -- won't do anything in case of concurrent issues.")
            return
        topcard = self.discard.pop()
        random.shuffle(discard)
        self.deck = self.discard + self.deck
        self.discard = [topcard]

    def end_game(self):
        if not self.lock.locked():
            print("Not locked -- won't do anything in case of concurrent issues.")
            return
        for player in self.players:
            self.remove_player(player)
        self.reset_state()

    def remove_player(self, player):
        if not self.lock.locked():
            print("Not locked -- won't do anything in case of concurrent issues.")
            return
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

        self.wildcolor = ""
        self.direction = 1

        colors   = ["red", "yellow", "green", "blue"]
        numbers  = list(range(10)) + list(range(1, 10))
        specials = ["skip", "reverse", "draw 2"]      * 2
        #wilds    = ["", "draw 4"]                     * 4

        self.deck += [(color, str(number)) for color in colors for number in numbers]
        self.deck += [(color, special)     for color in colors for special in specials]
        #self.deck += [("wild", wildtype)   for wildtype in wilds]

    def move(self, stack1, stack2):
        pass

    def shuffle(self, stack):
        counter = 0
        max = 107

        while counter <= max:
            num = random.randint(counter, max)
            #print(num, ', ', counter, ', ', max)
            card = stack[num]
            stack[num] = stack[counter]
            stack[counter] = card
            counter += 1

    def merge(self):
        pass

    def deal(self, player):
        counter = 0
        hand = []
        while counter < DEAL_SIZE:
            num = random.randint(0, len(deck)-1)
            hand.append(deck[num].pop())
            counter += 1
        hands.append(hand)


def setup(client):
    client.add_cog(uno(client))

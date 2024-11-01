import discord

from collections import defaultdict
import random


class UnoException(Exception):
    pass

class UnoMessage:
    def __init__(self, content=None, view=None, is_ephemeral=False):
        self.content   = content
        self.view      = view
        self.ephemeral = is_ephemeral

    async def respond_to(self, interaction):
        kwargs = {'ephemeral': self.ephemeral}
        if self.content:
            kwargs['content'] = self.content
        if self.view:
            kwargs['view']    = self.view

        await interaction.response.send_message(**kwargs)

        if self.view:
            self.view.message = await interaction.original_response()

    async def send_to(self, messageable):
        msg = await messageable.send(content   = self.content,
                                     view      = self.view,
                                     ephemeral = self.ephemeral)

        if self.view and self.view is not ...:
            self.view.message = msg
                            
    @classmethod
    def from_uno_view(cls, view, is_ephemeral=False):
        return cls(view.content, view, is_ephemeral)


class UnoCard:
    def __init__(self, color, value = ""):
        self.color = color
        self.value = value
        self.wild_color = None

    def get_name(self, use_unicode=False):
        # the only utf-8 encoding I've found of rainbow flag that works on browser
        rainbow_flag = b'\xf0\x9f\x8f\xb3\xef\xb8\x8f\xe2\x80\x8d\xf0\x9f\x8c\x88'.decode()

        emojis = {  "red"    : ":heart:",
                    "yellow" : ":yellow_heart:",
                    "green"  : ":green_heart:", 
                    "blue"   : ":blue_heart:", 
                    "wild"   : ":gay_pride_flag:",
 
                    "0"      : ":zero:",
                    "1"      : ":one:",
                    "2"      : ":two:",
                    "3"      : ":three:",
                    "4"      : ":four:",
                    "5"      : ":five:",
                    "6"      : ":six:",
                    "7"      : ":seven:",
                    "8"      : ":eight:",
                    "9"      : ":nine:",
                    "skip"   : ":no_entry_sign:",
                    "reverse": ":cyclone:",
                    "draw 2" : ":bangbang:",
                    ""       : ":gay_pride_flag:",
                    "draw 4" : ":bangbang: :bangbang:" }

        unicode = { "red"    : "\u2764\ufe0f", # red heart
                    "yellow" : "\U0001F49B",   # yellow heart
                    "green"  : "\U0001F49A",   # green heart
                    "blue"   : "\U0001F499",   # blue heart
                    "wild"   : rainbow_flag,

                    "0"      : "0\ufe0f\u20e3", # zero
                    "1"      : "1\ufe0f\u20e3", # one
                    "2"      : "2\ufe0f\u20e3", # two
                    "3"      : "3\ufe0f\u20e3", # three
                    "4"      : "4\ufe0f\u20e3", # four
                    "5"      : "5\ufe0f\u20e3", # five
                    "6"      : "6\ufe0f\u20e3", # six
                    "7"      : "7\ufe0f\u20e3", # seven
                    "8"      : "8\ufe0f\u20e3", # eight
                    "9"      : "9\ufe0f\u20e3", # nine
                    "skip"   : "\U0001f6ab",    # no entry
                    "reverse": "\U0001f300",    # cyclone
                    "draw 2" : "\u203c",        # double exclamation
                    ""       : rainbow_flag,
                    "draw 4" : "\u203c \u203c" }# 2x double exclamation

        lookup = unicode if use_unicode else emojis 

        color_emoji = lookup[self.color]
        value_emoji = lookup[self.value]

        color_name = f"{self.color}{f' ({self.wild_color})' if self.is_wild() and self.wild_color else ''}"
        name = f"{color_emoji} {value_emoji} {color_name} {self.value}"

        return name

    def is_special(self):
        return not self.value.isdecimal()

    def is_wild(self):
        return self.color == 'wild'

    def can_play_on(self, card):
        wild_match  = self.is_wild()           or self.color == card.wild_color
        other_match = self.color == card.color or self.value == card.value
        return wild_match or other_match

    def set_wild_color(self, wild_color):
        if not self.is_wild():
            raise UnoException("You can't choose the color of a non-wild card!")
        if wild_color and wild_color not in ["red", "yellow", "green", "blue"]:
            raise UnoException("You can't choose a color not in the deck!")

        self.wild_color = wild_color

    @classmethod
    def deck(cls):
        colors   = ["red", "yellow", "green", "blue"]
        numbers  = [0] + list(range(1, 10)) * 2
        specials = ["skip", "reverse", "draw 2"] * 2
        wilds    = ["", "draw 4"] * 4

        deck  = [cls(color, str(number)) for color in colors for number in numbers]
        deck += [cls(color, special)     for color in colors for special in specials]
        deck += [cls("wild", wildtype)   for wildtype in wilds]

        return deck

# models logic for a game of Uno
# validate input for logic and relationships; nobody else should worry about the logic for these.
class UnoGameState:
    def __init__(self, parent):
        self.parent  = parent

        self.DEAL_SIZE = 7
        self.in_game = False
        self.deck    = UnoCard.deck()
        self.discard = []
        self.players = []
        self.hands   = {}
        self.kicks   = defaultdict(set)
        self.stops   = set()
        self.turn    = 0

        self.claimed_uno = set()
        self.wild_color = None
        self.direction = 1

    def add_player(self, player):
        # (21 numbers + 6 specials) * 4 colors + 8 wilds = 116 cards total; consider limiting max players for this
        if player in self.players:
            raise UnoException("You can't join a game twice :V")
        # TODO midgame joins
        if self.in_game:
            raise UnoException("Wait for the current game to end before joining.")

        self.players.append(player)
        self.hands[player] = []

    def remove_player(self, player):
        if player not in self.players:
            raise UnoException("You can't leave if you haven't joined!")

        if self.in_game:
            self.discard = self.hands[player] + self.discard
            del self.hands[player]

            if player in self.kicks:
                del self.kicks[player]
            for target in self.kicks:
                if player in self.kicks[target]:
                    self.kicks[target].remove(player)
            if player in self.stops:
                self.stops.remove(player)
            
            # handle turn order effects
            index = self.players.index(player)
            if index < self.turn:
                self.turn -= 1

            self.players.remove(player)

            if len(self.players) <= 1:
                return self.end_game("The game has ended: Not enough players.")
            if index == self.turn:
                return self.players[self.turn]
        else:
            self.players.remove(player)

    def start_game(self):
        if self.in_game:
            raise UnoException("Can't start a game already in progress.")
        if len(self.players) < 2:
            raise UnoException("Not enough players. Get at least two to play!")

        random.shuffle(self.deck)
        for player in self.players:
            self.draw_cards(player, self.DEAL_SIZE)
        while len(self.discard) < 1 or self.discard[-1].is_wild():
            self.discard.append(self.deck.pop())

        self.in_game = True

    def end_game(self, reason):
        if self.in_game:
            self.in_game = False
        return reason

    def votestop(self, player):
        if not self.in_game:
            raise UnoException("You can't stop a game that isn't going, silly!")
        if player not in self.players:
            raise UnoException("I'm sure the people playing are glad to know you want it to end.")

        threshold = len(self.players) // 2 + 1

        if player in self.stops:
            self.stops.remove(player)
            return False, len(self.stops), threshold

        self.stops.add(player)
        votestops = len(self.stops)
        if votestops > threshold:
            return self.end_game("The game has ended: Voted to stop.")

        return True, votestops, threshold

    def votekick(self, player, target):
        if not self.in_game:
            raise UnoException("You should probably wait until the game is started to start kicking people.")
        if player not in self.players:
            raise UnoException("I'm glad to know you want to kick that guy.")

        votekick_threshold = len(self.player) // 2 + 1

        if player in self.kicks[target]:
            self.kicks[target].remove(player)
            return False, len(self.kicks[target]), votekick_threshold, None

        self.kicks[target].add(player)
        next_player = None
        num_kicks = len(self.kicks[target])
        if num_kicks > votekick_threshold:
            next_player = self.remove_player(target)

        return True, num_kicks, votekick_threshold, next_player

    def next_turn(self):
        self.turn = (self.turn + self.direction) % len(self.players)

    def play_card(self, player, card_idx, wild_color=None):
        # TODO dependency injection; allow for house rules here
        # things like... 
        #   ... skip interrupts turn order; zero switch hands; stacking draw 2s / draw 4s; etc., etc.

        if not self.in_game:
            raise UnoException("You can't play if the game isn't running!")
        if self.players[self.turn] != player:
            raise UnoException("Wait for your turn!")

        hand = self.hands[player]
        card = hand[card_idx]
        if card.is_wild():
            if not wild_color and not card.wild_color:
                raise UnoException('You need to provide a color for your wild card!')
            else:
                wild_color = wild_color or card.wild_color
                card.set_wild_color(wild_color)
        if not card.can_play_on(self.discard[-1]):
            raise UnoException("You can't play that card!")

        hand.pop(card_idx)
        self.discard.append(card)

        if card.is_wild():
            self.wild_color = wild_color

        if len(self.hands[player]) == 0:
            return self.end_game(f"The game has ended: {player.mention} has won!")

        victim = None
        if card.value == "skip":
            self.next_turn()
            victim = self.players[self.turn]
        elif card.value == "reverse":
            self.direction *= -1
        elif card.value == "draw 2":
            self.next_turn()
            victim = self.players[self.turn]
            self.draw_cards(victim, 2)
        elif card.value == "draw 4":
            self.next_turn()
            victim = self.players[self.turn]
            self.draw_cards(victim, 4)

        self.next_turn()
        return victim

    def draw_cards(self, player, num_cards):
        drawn_cards = []
        for card in range(num_cards):
            if len(self.deck) == 0 and len(self.discard) > 1:
                self.reshuffle()
            if len(self.deck) == 0:
                break

            card = self.deck.pop()
            if card.is_wild():
                card.set_wild_color(None) # don't draw pre-colored wilds
            drawn_cards.append(card)
        self.hands[player].extend(drawn_cards)

        # reset claimed_uno flag if appropriate
        if len(self.hands[player]) > 1 and player in self.claimed_uno:
            self.claimed_uno.remove(player)

        return drawn_cards
    
    def uno(self, player, target):
        PUNISHMENT_CARDS = 4
        is_safe = target in self.claimed_uno

        valid_uno = True
        if len(self.hands[target]) != 1:
            valid_uno = False
            self.draw_cards(player, PUNISHMENT_CARDS)
        elif not is_safe:
            valid_uno = True
            if player != target:
                self.draw_cards(target, PUNISHMENT_CARDS)
            self.claimed_uno.add(target)
        
        return valid_uno, is_safe

    def reshuffle(self):
        topcard = self.discard.pop()
        random.shuffle(self.discard)
        self.deck = self.discard + self.deck
        self.discard = [topcard]

    def deck_empty(self):
        return len(self.deck) == 0 and len(self.discard) <= 1
import discord
from discord.ext import commands
import random


"""
Deck, Pile, Hand
Deck --> Hand, Draw
Hand --> Pile, Play
Pile --> Hand, Draw
Pile --> Deck, Restock
Deck --> Pile, Stock

Draw + Play, Stock --> Move()
Restock --> Merge() + Shuffle + Move()

Move(), transfers selected card from one stack onto the top of another stack
Shuffle(), rearranges cards into a random order in a selected stack
Merge(), combines two stacks into one
addPlayer(), adds a player to the game
remPlayer(), removes a player from the game
(remPlayer() Only to be performed by the player or the host)

!uno, help command
!uopen, opens a lobby
!ustart, starts a lobby
!ustop, stops a lobby
!ujoin, adds player to game
!uleave, removes player from game
!ukick [mention], begins votekick to remove mentioned player from the game


*d2 stacking


"""

class uno:
    def __init__(self, client):
        self.client = client
        
        STAR = "410660094083334155"
        DEAL_SIZE = 7

        global deck
        global pile
        global hands
        global host
        global playing
        global player_queue

        deck = []
        pile = []
        hands = {}
        host = None
        playing = False
        player_queue = []

        counter = 0
        max = 40
        while counter < max:
            card = [int(counter/10),  counter%10]
            #print(card)
            deck.append(card)
            if card[1] != 0:
                deck.append(card)
            counter += 1
        #print('---')

        counter = 0
        max = 24

        while counter < max:
            card = [int(counter/6), 10 + (counter%3)]
            #print(card)
            deck.append(card)
            counter += 1
        #print('---')

        counter = 0
        max = 8
        while counter < max:
            card = [4, 13 + (counter%2)]
            #print(card)
            deck.append(card)
            counter += 1


        #print('---')
        #print(deck,', Length: ', len(deck))
        #print('---')


            

    @commands.command()
    #@commands.cooldown(1, 30, commands.BucketType.user)
    async def uno(self):
        output = ""
        output += "*!ustart* - "
        
        await self.client.say(output)

    @commands.command(pass_context = True)
    async def uopen(self):

        if not playing:
            global player_queue
            global host

            host = ctx.message.author
            player_queue = []
            player_queue.append(host)
            await self.client.say("" + host.name + " has started an Uno lobby!\nType *!unjoin* to join")
        else:
            await self.client.say("There's already a game going, type *!ujoin* to join")

    @commands.command()
    async def ustart(self):

        global hands
        numPlayers = len(hands)

        counter = 0


        while counter < numPlayers:
            hand = []
            
            deal()
            counter += 1

        num = random.randint(0, len(deck))
        pile.append(deck[num])
        deck.remove(deck[num])

    @commands.command(pass_context = True)
    async def ustop(self):
        if ctx.message.author.id == STAR or ctx.message.author.name == "Aanon" or ctx.message.author == host:
            uno.leave(hands)
        else:
            await self.client.say("You don't have permission to do that!")
            return

    @commands.command(pass_context = True)
    async def ujoin(self):
        if not playing:
            u
        else:
            u
            

    @commands.command(pass_context = True)
    async def uleave(self):
        if ctx.message.author.id == STAR or ctx.message.author.name == "Aanon" or ctx.message.author == host:
            temp = []
            temp.append(ctx.message.author)
            uno.leave(temp)
        else:
            await self.client.say("You don't have permission to do that!")
            return
        
    @commands.command(pass_context = True)
    async def ukick(self, ctx):
        if ctx.message.author.id == STAR or ctx.message.author.name == "Aanon" or ctx.message.author == host:
            uno.leave(ctx.message.mentions)
        else:
            await self.client.say("You don't have permission to do that!")
            return

    




    
    def move(self, stack1, stack2):
        

    
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
        y

    def leave(self, users):

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

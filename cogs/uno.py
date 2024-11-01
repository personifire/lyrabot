import discord
from discord.ext import commands

import asyncio
import importlib

import lib.uno.controller

class Uno(commands.Cog):
    """ Runs a game of uno!

    Join or leave an uno lobby with other players, and start the game whenever you're ready.
    """

    def __init__(self, client):
        self.client = client
        self.games  = {} # map channel_id -> uno_game

        self.helpstr  = "```"
        self.helpstr += "!uno help               Prints this message\n"
        self.helpstr += "!uno start              Opens an Uno lobby\n"
        self.helpstr += "!uno view               Views the current game\n"
        self.helpstr += "!uno                    For when you only have one card left!\n"
        self.helpstr += "```"

    # It's easier to do this than to actually think about concurrency...
    async def cog_before_invoke(self, ctx):
        if ctx.channel.id in self.games:
            await self.games[ctx.channel.id].lock.acquire()

    async def cog_after_invoke(self, ctx):
        if ctx.channel.id in self.games:
            game = self.games[ctx.channel.id]

            if game.lock.locked():
                game.lock.release()
    
    async def cleanup_game(self, channel_id, reason=None):
        if channel_id in self.games:
            del self.games[channel_id]

        channel = self.client.get_channel(channel_id)
        if channel and reason:
            await channel.send(reason)

    @commands.group(case_insensitive = True)
    async def uno(self, ctx):
        """ Play a game of uno. Try `!uno start`! """
        if ctx.invoked_subcommand is None:
            if ctx.channel.id not in self.games:
                await ctx.send(self.helpstr)
            else:
                msg = self.games[ctx.channel.id].uno(ctx.author)
                if msg:
                    await ctx.send(msg)

    @uno.command(name="help")
    async def uno_help(self, ctx):
        "Prints this message."
        await ctx.send(self.helpstr)

    @uno.command(aliases=["open"])
    async def start(self, ctx):
        "Starts an Uno lobby."
        if ctx.channel.type == discord.ChannelType.private:
            return await ctx.send("Sorry, no private uno games!")
        if ctx.channel.id in self.games:
            return await ctx.send("You can't run two Uno lobbies in the same channel!")

        game = lib.uno.controller.UnoController(self, ctx.channel.id)
        self.games[ctx.channel.id] = game

        lobby_msg = game.get_lobby_msg()
        await lobby_msg.send_to(ctx)

    @uno.command()
    async def view(self, ctx):
        if ctx.channel.id in self.games:
            if self.games[ctx.channel.id].gamestate.in_game:
                message = self.games[ctx.channel.id].get_gamestate_msg()
                return await message.send_to(ctx)
            return await ctx.send("You can't view a game that hasn't started yet!")
        return await ctx.send("You can't view a game that isn't going!")

    @uno.command()
    @commands.has_guild_permissions(administrator=True)
    async def end(self, ctx):
        await self.games[ctx.channel.id].die(": (killed by admin)") # TODO this is empty; likely getting removed on death
        del self.games[ctx.channel.id]
        return await ctx.send("Uno game has ended early (killed by admin).")

    def cog_unload(self):
        importlib.reload(lib.uno.controller)
        importlib.reload(lib.uno.models)
        importlib.reload(lib.uno.views)

# old messages
"""
send("There's no game to leave!")
send("Too few players left. Game's gonna have to end early!")
send(ctx.author.name + " has left the game. " + str(len(self.players)) + " players remain.")

send("Let's wait for one of the players to start, yes?")
send("Putting the top card on the discard! " + self.card_name(card))

send('You can only vote to end the game once! Try "!uno leave" to leave early.')
send(ctx.author.name + " has voted to end the game. " + 

send("You can only vote to kick someone once!")
send(ctx.author.name + " has voted to kick " + player.name + ". " +

send("You need to select a card to play.")
send("Try a number, instead.")
send("Try a number that makes sense, instead.")

send("Wait for the game to start before drawing!")
send("Wait for your turn, " + player.name + "!")
send("You can't draw that, try a number instead.")
send("Try a more reasonable number, instead.")

send("Wait for the game to start before looking at your hand!")
send("You can't look at your hand if you're not in the game!")
send("Your hand has been sent, " + ctx.author.name + ". Check your messages!")
"""

async def setup(client):
    await client.add_cog(Uno(client))

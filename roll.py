import discord
from discord.ext import commands

import random
import importlib

import roll_lib.parser

class roll(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(7, 10, commands.BucketType.user)
    async def roll(self, ctx, *args):
        string = " ".join(args)
        try:
            rollexpr = roll_lib.parser.parser(string)
            rollval  = rollexpr.evaluate()
        except Exception as e:
            errormsg = "I had trouble rolling that! ```" + str(e) + "```"
            await ctx.channel.send(errormsg)
            raise e

        value = 0
        for die in rollval:
            value += die

        await ctx.channel.send(ctx.author.mention + ", you rolled: " + str(value) + ". No, don't ask me to explain that.")


    def cog_unload(self):
        importlib.reload(roll_lib.lexer)
        importlib.reload(roll_lib.parser)
        importlib.reload(roll_lib.parsetree)



def setup(client):
    client.add_cog(roll(client))

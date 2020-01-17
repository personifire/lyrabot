import discord
from discord.ext import commands
import random

import roll.parser

class roll(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(7, 10, commands.BucketType.user)
    async def roll(self, ctx, *args):
        string = " ".join(args)
        rollexpr = roll.parser(string)
        rollval  = rollexpr.evaluate()

        value = 0
        for die in rollval:
            value += die

        await ctx.channel.send(ctx.author.mention + ", you rolled: " + str(value) + ". No, don't ask me to explain that.")



def setup(client):
    client.add_cog(fun(client))

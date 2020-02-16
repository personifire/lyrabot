import discord
from discord.ext import commands

import random
import importlib
import json
import os

import roll_lib.parser

SAVE_DIR      = "data/"
SAVE_FILENAME = SAVE_DIR + "saved_rolls.json"
SAVE_BACKUP   = SAVE_DIR + "saved_rolls.json.bak"

class roll(commands.Cog):
    def __init__(self, client):
        self.client = client

        # create empty file at location if it does not exist
        if not os.path.isdir(SAVE_DIR):
            os.mkdir(SAVE_DIR)

    @commands.command()
    async def roll(self, ctx, *, rollstring):
        try:
            rollexpr = roll_lib.parser.parser(rollstring)
            rolls    = rollexpr.roll()
        except Exception as e:
            errormsg = "I had trouble rolling that! ```" + str(e) + "```"
            await ctx.channel.send(errormsg)
            raise e

        value = 0
        for die in rolls:
            value += die

        await ctx.channel.send(ctx.author.mention + ", you rolled: " + str(value) + " " + str(rolls))



    @commands.command()
    async def roll_save(self, ctx, rollname, *, rollstring):
        await self.roll(ctx, rollstring=rollstring)

        saved = self.get_saved_rolls()
        if saved is None:
            saved = {}
        if str(ctx.author.id) not in saved:
            saved[str(ctx.author.id)] = {}
        saved[str(ctx.author.id)][rollname] = rollstring

        self.set_saved_rolls(saved)
        await ctx.channel.send("Roll saved!")



    @commands.command()
    async def roll_load(self, ctx, rollname):
        saved = self.get_saved_rolls()
        if saved and str(ctx.author.id) in saved and rollname in saved[str(ctx.author.id)]:
            await self.roll(ctx, rollstring=saved[str(ctx.author.id)][rollname])
        else:
            print("roll_load could not find id " + str(ctx.author.id) + " roll '" + rollname + "' in " + str(saved))
            await ctx.channel.send("I don't remember you saving that roll, before...")



    @commands.command()
    async def roll_delete(self, ctx, rollname):
        saved = self.get_saved_rolls()
        if saved and str(ctx.author.id) in saved and rollname in saved[str(ctx.author.id)]:
            del saved[str(ctx.author.id)][rollname]
            self.set_saved_rolls(saved)
            await ctx.channel.send("Roll deleted!")
        else:
            print("roll_delete could not find id " + str(ctx.author.id) + " roll '" + rollname + "' in " + str(saved))
            await ctx.channel.send("Can't delete what isn't saved!")



    @commands.command()
    async def roll_list(self, ctx):
        saved = self.get_saved_rolls()
        if saved and str(ctx.author.id) in saved and len(saved[str(ctx.author.id)]) > 0:
            message = "```"
            for rollname, roll in saved[str(ctx.author.id)].items():
                message += "{:<30}".format(rollname) + roll
            message += "```"
            await ctx.channel.send(message)
        else:
            print("roll_list could not find any rolls for id " + str(ctx.author.id) + " in " + str(saved))
            await ctx.channel.send("Pretty sure you don't have any saved rolls!")



    def get_saved_rolls(self):
        try:
            with open(SAVE_FILENAME, "r") as readfile:
                rolls = json.load(readfile)
        except FileNotFoundError:
            return None

        return rolls

    def set_saved_rolls(self, rolls):
        with open(SAVE_BACKUP, "w") as writefile:
            json.dump(rolls, writefile)
        os.rename(SAVE_BACKUP, SAVE_FILENAME)


    def cog_unload(self):
        importlib.reload(roll_lib.lexer)
        importlib.reload(roll_lib.parser)
        importlib.reload(roll_lib.parsetree)



def setup(client):
    client.add_cog(roll(client))

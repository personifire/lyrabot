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

class diceroll(commands.Cog):
    """ Dice rolling functionality!

    Capable of saving custom dice rolls on a per-user basis.
    """

    def __init__(self, client):
        self.client = client

        # create empty file at location if it does not exist
        if not os.path.isdir(SAVE_DIR):
            os.mkdir(SAVE_DIR)

    @commands.command()
    async def roll(self, ctx, *, rollstring):
        """ Rolls some dice

        Understands most standard dice notation
        Examples:
            1d10 + 5
            2d20 drop highest + 9
            3d20 drop 2 - 1
            (d6)d10
        """
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



    @commands.command(aliases = ["roll-save", "rollsave", "roll_sv", "roll-sv"])
    async def roll_save(self, ctx, rollname, *, rollstring):
        """ Saves a roll

        Rolls a given set of dice, then saves it under a custom alias for you
        Will overwrite previously saved rolls under the same name
        """
        await self.roll(ctx, rollstring=rollstring)

        saved = self.get_saved_rolls()
        if saved is None:
            saved = {}
        if str(ctx.author.id) not in saved:
            saved[str(ctx.author.id)] = {}
        saved[str(ctx.author.id)][rollname] = rollstring

        self.set_saved_rolls(saved)
        await ctx.channel.send("Roll saved!")



    @commands.command(aliases = ["roll-load", "rollload", "roll_ld", "roll-ld"])
    async def roll_load(self, ctx, *, rollname):
        """ Looks up and rolls a saved roll """
        saved = self.get_saved_rolls()
        if saved and str(ctx.author.id) in saved and rollname in saved[str(ctx.author.id)]:
            await self.roll(ctx, rollstring=saved[str(ctx.author.id)][rollname])
        else:
            print("roll_load could not find id " + str(ctx.author.id) + " roll '" + rollname + "' in " + str(saved))
            await ctx.channel.send("I don't remember you saving that roll, before...")



    @commands.command(aliases = ["roll-delete", "rolldelete", "roll_del", "roll-del"])
    async def roll_delete(self, ctx, *, rollname):
        """ Looks up and deletes a saved roll """
        saved = self.get_saved_rolls()
        if saved and str(ctx.author.id) in saved and rollname in saved[str(ctx.author.id)]:
            del saved[str(ctx.author.id)][rollname]
            self.set_saved_rolls(saved)
            await ctx.channel.send("Roll deleted!")
        else:
            print("roll_delete could not find id " + str(ctx.author.id) + " roll '" + rollname + "' in " + str(saved))
            await ctx.channel.send("Can't delete what isn't saved!")



    @commands.command(aliases = ["roll-list", "rolllist", "roll_ls", "roll-ls"])
    async def roll_list(self, ctx):
        """ Lists all available saved rolls """
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
    client.add_cog(diceroll(client))

import discord
from discord.ext import commands

class react:
    def __init__(self, client):
        self.client = client


    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.channel)
    async def react(self):
        output = ""
        output += "angery, blep, dab, default, excite, floss, flyra, lyravator, scared, swiggityswooty, thonk"
        await self.client.say(output)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def apples(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "apples:525139683395764244")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<:apples:525139683395764244>")


    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def angery(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "ANGERY:525142734684815370")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<a:ANGERY:525142734684815370>")

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blep(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "blep:532497085254205450")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<:blep:532497085254205450>")

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dab(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "dab:531755608467046401")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<:dab:531755608467046401>")

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def default(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "default:531762705128751105")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<a:default:531762705128751105>")
            

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def excite(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "excite:531769597108551691")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<a:excite:531769597108551691>")

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def floss(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "floss:531762332121169930")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<a:floss:531762332121169930>")


    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def flyra(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "flyra:531755302996148237")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<a:flyra:531755302996148237>")


    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lyravator(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "lyravator:531772198910689280")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<a:lyravator:531772198910689280>")


    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def scared(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "scared:532497591426875394")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<:scared:532497591426875394>")


    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def swiggityswooty(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "swiggityswooty:531779000251580416")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<a:swiggityswooty:531779000251580416>")

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def thonk(self, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], "thonk:532534756093460481")
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say("<:thonk:532534756093460481>")

        
def setup(client):
    client.add_cog(react(client))

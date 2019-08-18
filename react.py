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
    
    async def add_emote(self, react_name, emote_name, ctx):
        if ctx.message.mentions:
            i = len(self.client.messages)
            found = False
            while i > 0 and not found:
                i -= 1
                if self.client.messages[i].author == ctx.message.mentions[0]:
                    found = True
            if found:
                await self.client.add_reaction(self.client.messages[i], react_name)
            else:
                await self.client.say("*shrugs*")
        else:
            await self.client.say(emote_name)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def apples(self, ctx):
        await self.add_emote("apples:525139683395764244", "<:apples:525139683395764244>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def angery(self, ctx):
        await self.add_emote("ANGERY:525142734684815370", "<a:ANGERY:525142734684815370>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blep(self, ctx):
        await self.add_emote("blep:532497085254205450", "<:blep:532497085254205450>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dab(self, ctx):
        await self.add_emote("dab:531755608467046401", "<:dab:531755608467046401>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def default(self, ctx):
        await self.add_emote("default:531762705128751105", "<a:default:531762705128751105>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def excite(self, ctx):
        await self.add_emote("excite:531769597108551691", "<a:excite:531769597108551691>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def floss(self, ctx):
        await self.add_emote("floss:531762332121169930", "<a:floss:531762332121169930>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def flyra(self, ctx):
        await self.add_emote("flyra:531755302996148237", "<a:flyra:531755302996148237>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lyravator(self, ctx):
        await self.add_emote("lyravator:531772198910689280", "<a:lyravator:531772198910689280>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def scared(self, ctx):
        await self.add_emote("scared:532497591426875394", "<:scared:532497591426875394>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def swiggityswooty(self, ctx):
        await self.add_emote("swiggityswooty:531779000251580416", "<a:swiggityswooty:531779000251580416>", ctx)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def thonk(self, ctx):
        await self.add_emote("thonk:532534756093460481", "<:thonk:532534756093460481>", ctx)


def setup(client):
    client.add_cog(react(client))

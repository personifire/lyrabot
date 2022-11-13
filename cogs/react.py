import discord
from discord.ext import commands

emotes = [   # emote name         # emote id
            #("apples",           "<:apples:525139683395764244>"),
            ("angery",           "<a:ANGERY:525142734684815370>"),
            ("blep",             "<:blep:532497085254205450>"),
            ("dab",              "<:dab:531755608467046401>"),
            ("default",          "<a:default:531762705128751105>"),
            #("excite",           "<a:excite:531769597108551691>"),
            ("floss",            "<a:floss:531762332121169930>"),
            ("flyra",            "<a:flyra:531755302996148237>"),
            ("lyravator",        "<a:lyravator:531772198910689280>"),
            ("scared",           "<:scared:532497591426875394>"),
            ("swiggityswooty",   "<a:swiggityswooty:531779000251580416>"),
            ("thonk",            "<:thonk:532534756093460481>"),
         ]

class react(commands.Cog):
    """ Reacts or posts a few emojis! 

    Use `!apples` or others to post an emoji
    Mention a user to react to their latest post
    """
    def __init__(self, client):
        self.client = client
    #    self.reacts = []
    #    # register all the emotes -- works, but adds commands to client instead of cog
    #    for emote in emotes:
    #        self.reacts.append(
    #            commands.command(name = emote[0])( # something usually adds these commands. Maybe a superclass thing?
    #                commands.cooldown(1, 15, commands.BucketType.channel)(
    #                    self.emote_func(emote[1])
    #                )
    #            )
    #        )
    #        client.add_command(self.reacts[-1])
    #    print(list(map(lambda cmd: cmd.name, self.get_commands())))
    #    print(list(map(lambda cmd: cmd.name, self.reacts)))

    #def emote_func(self, emote):
    #    async def emote_command(self, ctx):
    #        await self.add_emote(emote, ctx)
    #    return emote_command


    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.channel)
    async def react(self, ctx):
        """ Lists all emotes available """
        output = ""
        for emote in emotes:
            output += emote[0] + ", "
        await self.client.say(output)
    
    async def add_emote(self, emote_name, ctx):
        if ctx.message.mentions:
            for msg in reversed(self.client.messages):
                if msg.author == ctx.message.mentions[0]:
                    msg.add_reaction(emote_name)
                    return
            await ctx.channel.send("*shrugs*")
        else:
            await ctx.channel.send(emote_name)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def apples(self, ctx):
        await self.add_emote("<:apples:525139683395764244>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def angery(self, ctx):
        await self.add_emote("<a:ANGERY:525142734684815370>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blep(self, ctx):
        await self.add_emote("<:blep:532497085254205450>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dab(self, ctx):
        await self.add_emote("<:dab:531755608467046401>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def default(self, ctx):
        await self.add_emote("<a:default:531762705128751105>", ctx)

    #@commands.command(hidden=True)
    #@commands.cooldown(1, 3, commands.BucketType.user)
    #async def excite(self, ctx):
    #    await self.add_emote("<a:excite:531769597108551691>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def floss(self, ctx):
        await self.add_emote("<a:floss:531762332121169930>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def flyra(self, ctx):
        await self.add_emote("<a:flyra:531755302996148237>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def lyravator(self, ctx):
        await self.add_emote("<a:lyravator:531772198910689280>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def scared(self, ctx):
        await self.add_emote("<:scared:532497591426875394>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def swiggityswooty(self, ctx):
        await self.add_emote("<a:swiggityswooty:531779000251580416>", ctx)

    @commands.command(hidden=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def thonk(self, ctx):
        await self.add_emote("<:thonk:532534756093460481>", ctx)

async def setup(client):
    await client.add_cog(react(client))

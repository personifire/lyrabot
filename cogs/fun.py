import discord
from discord.ext import commands
import random

class fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.star_id = 410660094083334155

        self.russianCount = random.randint(0, 5)


    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def boop(self, ctx):
        """ boop! """
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
            if self.client.user in ctx.message.mentions:
                await ctx.channel.send('but ' + ctx.author.display_name + ', that\'s *lewd!*')
                return
            elif "www." in ctx.message.content or ".org" in ctx.message.content or ".com" in ctx.message.content or ".xxx" in ctx.message.content:
                user = ctx.author
        else:
            if '@everyone' in ctx.message.content.lower():
                await ctx.channel.send('That\'s a *lot* of boops')
                return
            user = ctx.author
        if self.star_id == user.id:
            await ctx.channel.send('*boops* <@' + str(self.star_id) + '> *sensually*')
        else:
            await ctx.channel.send('*boops* ' + user.display_name)

    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def flip(self, ctx):
        """ Flips a coin """
        coin = random.randint(0, 99)
        result = "Heads"
        if coin < 50:
            result = "Tails"
        await ctx.channel.send(result)

    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def kill(self, ctx):
        """ \N{HOCHO} """
        output = ""
        data = [
                "*banishes {} to the moon*",
                "*banishes {} to the sun*",
                "*banishes {} to Klugetown*",
                "*bucks {} in the jaw*",
                "*dunks {} into the Stream of Silence until they stop moving*",
                "*dunks {} into the Mirror Pool until they stop moving*",
                "*feeds {} to the timberwolves*",
                "*feeds {} to the hydra*",
                "*feeds {} to the parasprites*",
                "*feeds {} to the puckwudgies*",
                "*feeds {} to the tatzlewurm*",
                "*feeds {} to a pack of ravenous kirin*",
                "*feeds {} to ahuizotl*",
                "*feeds {} to the sphinx*",
                "*feeds {} to l̸͈̰̮͖̝̞̟̹̝̎̆̈́̉̏́o͋̍̊ͭ҉̡͍̮̫̤̠͔̬͔̠̳̪̞̣̟͙̥̯́͞ọ̷̶̯͍̖̟̱̼͎͖͙̠̤̪̈́̈́͊ͥ̒ͪ̅̌ͮ̚n̶̨̮̱̥͖̹̊ͩ͌̐ͩ́̆̂ͨ͠͠ą̶̛̜͚̱̹͈̤̐ͮ̅̐͌ͥͬ̒͗ͮͮ̍*",
                "*scruffinates {}*",
                "*smashes {}'s face with a hoof*",
                "*sells {} to the Diamond Dogs*",
                "*sends {} to RGRE*",
                "*sends {} to 4channel*",
                "*suffocates* {} *in her chest fluff*",
                "*ties a brick to {} to let them swim with the seaponies*",
                "*throws {} off of Twilight's castle*",
                "*throws {} off the side of Canterlot*",
                "*throws {} to the gas chamber*",
                "*traps {} in a 1-second long time loop*",
                "*transforms {} into a mare and sends them to SPG*",
                "*transforms {} into a filly and sends them to MLPG*",
                "*transforms {} into an anonfilly and sends them to Scruffy*",
                "*u̴̠͕̹̮͔ͤ̂̍͊̀̀͡ṇ̨͉͎̩̬̪͔̔ͭͨ̑͂͑͑͐ͩ̇̾̂ͭ͜s̢̻̖̼̙͉̲͍̖͕̜͚̥͚̍̇͂ͫ͜͞iͤ̂ͤ͌͆̍̌ͫ̍͑͊͛̓̚̚͝͏̺̖͉̺͇̫̯̻̝̗͈͓̪͙̰̀͘͝n̨̛̛̞͙̐̅̎̆͒̒̽̾͑́̚͠ͅg̬̤̺̻̖̞̞͉̖̱̯̪̗̙͇̩̻̞ͬ̀ͭ̇͛ͤͨ̀͢͠s̞̦̱̱͍̬̫̊ͬ͐ͤ̀ͩͯ͗̀ͦ͞ {}*",
            ]

        output = random.choice(data)

        if "everyone" in ctx.message.content:
            output = "I'd rather not be banished to the moon thank you very much"
        elif not ctx.message.mentions:
            output = output.format(ctx.message.author.display_name)
        elif self.client.user in ctx.message.mentions or self.star_id == ctx.message.mentions[0].id:
            output = output.format(ctx.message.author.display_name)
        elif ctx.author in ctx.message.mentions:
            output = ":doughnut:"
        else:
            output = output.format(ctx.message.mentions[0].display_name)
        await ctx.channel.send(output)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pop(self, ctx):
        """ pop """
        pops = ["glim", "shy", "twi", "rara", "pink", "aj", "dash", "spike", "sun", "lyra"]
        output = "pop/" + random.choice(pops) + ".png"
        async with ctx.channel.typing():
            await ctx.channel.send(file=discord.File(output, "pop.png"))


    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def rr(self, ctx):
        """ Russian roulette! """
        if self.russianCount > 0:
            await ctx.channel.send(ctx.message.author.mention + ' *click*')
            self.russianCount -= 1
        else:
            await ctx.channel.send(ctx.message.author.mention + ' **BANG**')
            self.russianCount = random.randint(0, 5)

    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def tableflip(self, ctx):
        """ flips a table """
        await ctx.channel.send('(ノ°Д°）ノ︵ ┻━┻')



def setup(client):
    client.add_cog(fun(client))

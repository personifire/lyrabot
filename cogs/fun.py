import asyncio
from datetime import datetime, timedelta
import random
import re

import discord
from discord.ext import commands

class fun(commands.Cog):
    """ Miscellaneous things that one might label "fun" """
    def __init__(self, client):
        self.client = client
        self.star_id = 410660094083334155

        self.russian_count = random.randint(0, 5)
        self.rr_victims = {}


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content and not message.author.bot:
            if message.content == "Can I boop you?":
                await message.channel.send("*gasp* but that's lewd!")

            elif "screwbot " in message.content.lower() or " screwbot" in message.content.lower() or "screwbot" == message.content.lower():
                await message.channel.send("<a:headcannonL:532554000818634783><:screwbot:532520479290818560><a:headcannonR:532554001321951262>")

            elif 'hands ' in message.content.lower() or ' hands' in message.content.lower() or 'hands' == message.content.lower():
                await message.channel.send("<:mfw:532548719510552586>")

            elif ':' in message.content.lower():
                new = message.content.lower().replace(":", "")
                if "apples" in new:
                    await message.channel.send("<:apples:525139683395764244>")
                elif "angery" in new:
                    await message.channel.send("<a:angery:525142734684815370>")
                elif "blep" in new:
                    await message.channel.send("<:blep:532497085254205450>")
                elif "dab" in new:
                    await message.channel.send("<:dab:531755608467046401>")
                elif "default" in new:
                    await message.channel.send("<a:default:531762705128751105>")
                elif "flyra" in new:
                    await message.channel.send("<a:flyra:531755302996148237>")
                elif "lyravator" in new:
                    await message.channel.send("<a:lyravator:531772198910689280>")
                elif "scared" in new:
                    await message.channel.send("<:scared:532497591426875394>")
                elif "swiggityswooty" in new:
                    await message.channel.send("<a:swiggityswooty:531779000251580416>")
                elif "thonk" in new:
                    await message.channel.send("<:thonk:532534756093460481>")

            elif 'lyra' in message.content.lower() and 'play' in message.content.lower():
                if 'despacito' in message.content.lower():
                    await message.channel.send('https://youtu.be/kJQP7kiw5Fk')
                elif 'sinking' in message.content.lower() and 'ships' in message.content.lower():
                    await message.channel.send(' https://youtu.be/Tw09Lrf4EQc')
                elif 'lullaby for a princess' in message.content.lower():
                    await message.channel.send('https://youtu.be/H4tyvJJzSDk')
                elif 'hold on' in message.content.lower():
                    await message.channel.send('https://youtu.be/ryi-Iy0VyWs')
                elif 'wow glimmer' in message.content.lower():
                    await message.channel.send('https://youtu.be/12_WnaPmPI0')
                elif 'discord' in message.content.lower():
                    await message.channel.send('https://youtu.be/xPfMb50dsOk')
                elif 'imagine' in message.content.lower():
                    await message.channel.send('https://youtu.be/YkgkThdzX-8')
                    

            if self.client.user.display_name.lower() in message.content.lower():
                if 'hi' in message.content.lower() or 'hello' in message.content.lower() or 'sup' in message.content.lower():
                    await message.channel.send('Hi ' + message.author.display_name + '!')
                if 'rolls' in message.content.lower():
                    await message.channel.send("<:smuglyra:543975500562038784>")
            if "u lil shid" in message.content.lower():
                await message.channel.send('*pbbbtthhhhhh*')
            if "hmmnah.mp4" in message.content.lower():
                await message.channel.send(file=discord.File("files/hmmnah.mp4"))
            if "lyra" in message.content.lower() and "best" in message.content.lower() and "not" not in message.content.lower():
                await message.channel.send('*blushes*')


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
        pops = ["glim", "shy", "twi", "rara", "pink", "aj", "dash", "spike", "sun", "lyra", "ab", "sb"]
        output = "files/pop/" + random.choice(pops) + ".png"
        async with ctx.channel.typing():
            await ctx.channel.send(file=discord.File(output, "pop.png"))


    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def rr(self, ctx, target:discord.User = None):
        """ Russian roulette! """
        # update victims list -- note, this is not guild-specific
        now = datetime.now()
        victim_window = timedelta(minutes=5) # time willing participants open themselves up to get fucked for
        self.rr_victims = {victim: deadline for victim, deadline in self.rr_victims.items() if now < deadline}
        self.rr_victims[ctx.author] = now + victim_window

        # _rr_helper doesn't timeout if passed 0 duration; kinda dirty, but lets us do perms checking in here, rather than there
        can_timeout = False
        if type(ctx.me) == discord.Member:
            if ctx.me.guild_permissions.moderate_members:
                can_timeout = True

        timeout_duration = 30 if can_timeout else 0 

        if target:
            if target == ctx.me:
                # you lose!
                self.russian_count = 0
                await self._rr_helper(ctx.channel, ctx.author, 4 * timeout_duration, ' **BANG BANG BANG BANG**')
            elif target in self.rr_victims: 
                safe = await self._rr_helper(ctx.channel, target, timeout_duration)

                if safe:
                    await ctx.send(ctx.author.mention + " You're safe... for now, you murderer.")
                else:
                    bang_msg = f' {"*click* " * self.russian_count}**BANG**'
                    self.russian_count = 0
                    await self._rr_helper(ctx.channel, ctx.author, timeout_duration, bang_msg)
            else: 
                msgs = [" Don't point that thing at a random innocent!", " At least point it at somebody who's playing right now!", " Nope!", " Hmmm, nah."]
                await ctx.send(ctx.author.mention + random.choice(msgs))

            return # don't run anything else if targetted

        # self-target
        await self._rr_helper(ctx.channel, ctx.author, timeout_duration)

    async def _rr_helper(self, channel, victim, timeout_duration, custom_bang=None):
        if self.russian_count > 0:
            await channel.send(victim.mention + ' *click*')
            self.russian_count -= 1
            return False
        else:
            await channel.send(victim.mention + (custom_bang or ' **BANG**'))
            self.russian_count = random.randint(0, 5)

            if timeout_duration:
                await asyncio.sleep(10)
                await victim.timeout(timedelta(seconds=timeout_duration))
            return True

    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def tableflip(self, ctx):
        """ flips a table """
        await ctx.channel.send('(ノ°Д°）ノ︵ ┻━┻')


    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def avatar(self, ctx, user:discord.User = None):
        """ Gets a link to the mentioned user's avatar """
        if user:
            if isinstance(user, str):
                await ctx.send("I don't think I know that one, sorry!")
            else:
                await ctx.send(user.display_avatar)
        elif len(ctx.message.mentions) == 0:
            return await ctx.channel.send(ctx.author.display_avatar)
        else:
            async with ctx.channel.typing():
                for user in ctx.message.mentions:
                    await ctx.channel.send(user.display_avatar)

    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def emote(self, ctx, name):
        """ Gets a link to the image for the given emoji """
        match = re.match(r"<(a?):([a-zA-Z0-9\_]+):([0-9]+)?>$", name)

        if match:
            anim = match.group(1)
            name = match.group(2)
            id   = match.group(3)
            emote = discord.PartialEmoji(name = name, animated = anim, id = id)

            await ctx.channel.send(emote.url)
        else:
            await ctx.channel.send("Sorry, I can't find that one!")


async def setup(client):
    await client.add_cog(fun(client))

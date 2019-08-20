import discord
from discord.ext import commands
import random

class fun:
    def __init__(self, client):
        self.client = client
        self.star_id = "410660094083334155"

        self.russianCount = random.randint(0, 5)


    @commands.command(pass_context=True)
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def boop(self, ctx):
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
            if self.client.user in ctx.message.mentions:
                user = self.client.user
            elif "www." in ctx.message.content or ".org" in ctx.message.content or ".com" in ctx.message.content or ".xxx" in ctx.message.content:
                user = ctx.message.author
        else:
            if '@everyone' in ctx.message.content.lower():
                await self.client.say('That\'s a *lot* of boops')
                return
            user = ctx.message.author
        if self.star_id in user.id:
            await self.client.say('*boops* <@' + self.star_id + '> *sensually*')
        else:
            await self.client.say('*boops* ' + user.display_name)

    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def flip(self):
        coin = random.randint(0, 99)
        result = "Heads"
        if coin < 50:
            result = "Tails"
        await self.client.say(result)

    @commands.command(pass_context = True)
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def kill(self, ctx):
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
        elif self.client.user in ctx.message.mentions or self.star_id in ctx.message.mentions[0].id:
            output = output.format(ctx.message.author.display_name)
        elif ctx.message.author in ctx.message.mentions:
            output = ":doughnut:"
        else:
            output = output.format(ctx.message.mentions[0].display_name)
        await self.client.say(output)

    @commands.command(pass_context = True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pop(self, ctx):
        await self.client.send_typing(ctx.message.channel)

        pops = ["glim", "shy", "twi", "rara", "pink", "aj", "dash", "spike", "sun", "lyra"]
        output = "pop/" + random.choice(pops) + ".png"

        await self.client.send_file(ctx.message.channel, output)


    @commands.command(pass_context = True)
    @commands.cooldown(7, 10, commands.BucketType.user)
    async def roll(self, ctx, *args):
        await self.client.send_typing(ctx.message.channel)
        if args[0].isdigit():

            if int(args[0]) > 0 and len(args) == 1:
                ranNum =  random.randint(1, int(args[0]))
                output = ctx.message.author.mention
                output += ": " + str(ranNum)
                await self.client.say(ctx.message.author.mention + ': ' + str(ranNum))

            elif int(args[0]) > 0:
                skip = True
                ranNum = int(random.randint(1, int(args[0])))
                output = str(ranNum)
                mod = []
                for arg in args:
                    if skip:
                        skip = False
                    else:
                        if arg[0:1].lower() == 'x' and arg[1:].isdigit():
                            for x in range(int(arg[1:])-1):
                                temp = random.randint(1, int(args[0]))
                                for x in range(len(mod)):
                                    ranNum += mod[x]
                                ranNum += temp
                                output += ", " + str(temp)

                        elif arg[0:1].lower() == '+' and arg[1:].isdigit():
                            mod.append(int(arg[1:]))
                            ranNum += int(arg[1:])

                        elif arg[0:1].lower() == '-' and arg[1:].isdigit():
                            mod.append(int(arg[1:]))
                            ranNum -= int(arg[1:])

                if int(ranNum) <= 0:
                    ranNum = 1
                output += (": " +  str(ranNum))
                await self.client.say(ctx.message.author.mention + ": " + output)

            else:
                await self.client.say("Uhm, I don't think I can roll that...")
                
        else:
            await self.client.say("Uhm, I don't think I can roll that...")


    @commands.command(pass_context = True)
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def rr(self, ctx):
        if self.russianCount > 0:
            await self.client.say(ctx.message.author.mention + ' *click*')
            self.russianCount -= 1
        else:
            await self.client.say(ctx.message.author.mention + ' **BANG**')
            self.russianCount = random.randint(0, 5)

    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def tableflip(self):
        await self.client.say('(ノ°Д°）ノ︵ ┻━┻')



def setup(client):
    client.add_cog(fun(client))

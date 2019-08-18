import discord
from discord.ext import commands
import random

class fun:
    def __init__(self, client):
        self.client = client

        global STAR
        global LYRA

        STAR = "410660094083334155"
        LYRA = "495322560188252170"

        global russianCount
        russianCount = random.randint(0, 5)


    @commands.command(pass_context=True)
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def boop(self, ctx):
        if ctx.message.mentions:
            if self.client.user in ctx.message.mentions:
                await self.client.say('but ' + ctx.message.author.display_name + ', that\'s *lewd!*')
            elif str(STAR) in ctx.message.mentions[0].id:
                await self.client.say('*boops* <@' + STAR + '> *sensually*')
            elif "www." in ctx.message.content or ".org" in ctx.message.content or ".com" in ctx.message.content or ".xxx" in ctx.message.content:
                await self.client.say('*boops ' + ctx.message.author.name)                
            else:
                await self.client.say('*boops* ' + ctx.message.mentions[0].display_name)
        else:
            if '@everyone' in ctx.message.content.lower():
                await self.client.say('That\'s a *lot* of boops')
            elif ctx.message.author.id == STAR:
                await self.client.say('*boops* <@' + STAR + '> *sensually*')
            elif "www." in ctx.message.content or ".org" in ctx.message.content or ".com" in ctx.message.content or ".xxx" in ctx.message.content:
                await self.client.say('*boops ' + ctx.message.author.name) 
            else:
                await self.client.say('*boops* ' + ctx.message.author.display_name)


    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def flip(self):
        coin = random.randint(0, 99)
        result = "none"
        if coin < 50:
            result = "Tails"
        else:
            result = "Heads"
        await self.client.say(result)

    @commands.command(pass_context = True)
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def kill(self, ctx):
        output = ""
        data = []
        
        data.append("*banishes user to the moon*")
        data.append("*banishes user to the sun*")
        data.append("*banishes user to Klugetown*")
        data.append("*bucks user in the jaw*")
        data.append("*dunks user into the Stream of Silence until they stop moving*")
        data.append("*dunks user into the Mirror Pool until they stop moving*")
        data.append("*feeds user to the timberwolves*")
        data.append("*feeds user to the hydra*")
        data.append("*feeds user to the parasprites*")
        data.append("*feeds user to the puckwudgies*")
        data.append("*feeds user to the tatzlewurm*")
        data.append("*feeds user to a pack of ravenous kirin*")
        data.append("*feeds user to ahuizotl*")
        data.append("*feeds user to the sphinx*")
        data.append("*feeds user to l̸͈̰̮͖̝̞̟̹̝̎̆̈́̉̏́o͋̍̊ͭ҉̡͍̮̫̤̠͔̬͔̠̳̪̞̣̟͙̥̯́͞ọ̷̶̯͍̖̟̱̼͎͖͙̠̤̪̈́̈́͊ͥ̒ͪ̅̌ͮ̚n̶̨̮̱̥͖̹̊ͩ͌̐ͩ́̆̂ͨ͠͠ą̶̛̜͚̱̹͈̤̐ͮ̅̐͌ͥͬ̒͗ͮͮ̍*")
        data.append("*scruffinates user*")
        data.append("*smashes user's face with a hoof*")
        data.append("*sells user to the Diamond Dogs*")
        data.append("*sends user to RGRE*")
        data.append("*sends user to 4channel*")
        data.append("*suffocates* user *in her chest fluff*")
        data.append("*ties a brick to user to let them swim with the seaponies*")
        data.append("*throws user off of Twilight's castle*")
        data.append("*throws user off the side of Canterlot*")
        data.append("*throws user to the gas chamber*")
        data.append("*traps user in a 1-second long time loop*")
        data.append("*transforms user into a mare and sends them to SPG*")
        data.append("*transforms user into a filly and sends them to MLPG*")
        data.append("*transforms user into an anonfilly and sends them to Scruffy*")
        data.append("*u̴̠͕̹̮͔ͤ̂̍͊̀̀͡ṇ̨͉͎̩̬̪͔̔ͭͨ̑͂͑͑͐ͩ̇̾̂ͭ͜s̢̻̖̼̙͉̲͍̖͕̜͚̥͚̍̇͂ͫ͜͞iͤ̂ͤ͌͆̍̌ͫ̍͑͊͛̓̚̚͝͏̺̖͉̺͇̫̯̻̝̗͈͓̪͙̰̀͘͝n̨̛̛̞͙̐̅̎̆͒̒̽̾͑́̚͠ͅg̬̤̺̻̖̞̞͉̖̱̯̪̗̙͇̩̻̞ͬ̀ͭ̇͛ͤͨ̀͢͠s̞̦̱̱͍̬̫̊ͬ͐ͤ̀ͩͯ͗̀ͦ͞ user*")
        
        output = data[random.randint(0, len(data)-1)]
        
        if "everyone" in ctx.message.content:
            output = "I'd rather not be banished to the moon thank you very much"
        elif not ctx.message.mentions:
            output = output.replace("user", ctx.message.author.display_name)
        elif self.client.user in ctx.message.mentions or str(STAR) in ctx.message.mentions[0].id:
            output = output.replace("user", ctx.message.author.display_name)
        elif ctx.message.author in ctx.message.mentions:
            output = ":doughnut:"
        else:
            output = output.replace("user", ctx.message.mentions[0].display_name)
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
        global russianCount
        if russianCount > 0:
            await self.client.say(ctx.message.author.mention + ' *click*')
            russianCount -= 1
        else:
            await self.client.say(ctx.message.author.mention + ' **BANG**')
            russianCount = random.randint(0, 5)

    @commands.command()
    @commands.cooldown(2, 7, commands.BucketType.user)
    async def tableflip(self):
        await self.client.say('(ノ°Д°）ノ︵ ┻━┻')

        

def setup(client):
    client.add_cog(fun(client))

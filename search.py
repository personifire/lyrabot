import discord
from discord.ext import commands
import derpibooru
from derpibooru import Search, sort

class search:
    def __init__(self, client):
        self.client = client
        global key




    @commands.command(pass_context = True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def search(self, ctx, *args):
        await self.client.send_typing(ctx.message.channel)
        if not (ctx.message.channel.name == "lyra" or ctx.message.channel.name == "test" or ctx.message.channel.name == "nsfw"):
            await self.client.say("<#494919888629006356>")
            return
            
        if args:
            tags = ['']
            del tags[:]
            c1 = 0
            for tag in args:
                c2 = 0
                temp = ''
                for letter in tag:
                    if letter == '_':
                        temp += ' '
                    else:
                        temp += args[c1][c2]
                    c2 += 1
                tags.append(temp)
                c1 += 1

            global key
            
            if ctx.message.channel.name != "nsfw":
                if 'grimdark' in tags and 'explicit' in tags:
                    await self.client.say("How about *no* <:ew:532536050350948376>")
                elif 'explicit' in tags:
                    if 'lyra' in tags:
                        await self.client.say("Hey, at least take me out to dinner first!")
                    else:
                        await self.client.say("Ponies are NOT for sexual")
                elif 'grimdark' in tags:
                    await self.client.say("I'd rather not see that")
                if False:
                    return
                
                else:   
                    if len(tags) == 1:
                        for post in Search().key(key).query("-explicit", "-grimdark", "-anthro", tags[0]).sort_by(sort.RANDOM).limit(1):
                            await self.client.say(post.url)
                    elif len(tags) == 2:
                        for post in Search().key(key).query("-explicit", "-grimdark", "-anthro", tags[0], tags[1]).sort_by(sort.RANDOM).limit(1):
                            await self.client.say(post.url)
                    elif len(tags) == 3:
                        for post in Search().key(key).query("-explicit", "-grimdark", "-anthro", tags[0], tags[1], tags[2]).sort_by(sort.RANDOM).limit(1):
                            await self.client.say(post.url)
                    elif len(tags) == 4:
                        for post in Search().key(key).query("-explicit", "-grimdark", "-anthro", tags[0], tags[1], tags[2], tags[3]).sort_by(sort.RANDOM).limit(1):
                            await self.client.say(post.url)
                    elif len(tags) == 5:
                        for post in Search().key(key).query("-explicit", "-grimdark", "-anthro", tags[0], tags[1], tags[2], tags[3], tags[4]).sort_by(sort.RANDOM).limit(1):
                            await self.client.say(post.url)
            elif 'grimdark' in tags or 'anthro' in tags:
                await self.client.say("<:ew:532536050350948376>")
                
            else:                
                if len(tags) == 1:
                    for post in Search().key(key).query("-grimdark", "-anthro", tags[0]).sort_by(sort.RANDOM).limit(1):
                        await self.client.say(post.url)
                elif len(tags) == 2:
                    for post in Search().key(key).query("-grimdark", "-anthro", tags[0], tags[1]).sort_by(sort.RANDOM).limit(1):
                        await self.client.say(post.url)
                elif len(tags) == 3:
                    for post in Search().key(key).query("-grimdark", "-anthro", tags[0], tags[1], tags[2]).sort_by(sort.RANDOM).limit(1):
                        await self.client.say(post.url)
                elif len(tags) == 4:
                    for post in Search().key(key).query("-grimdark", "-anthro", tags[0], tags[1], tags[2], tags[3]).sort_by(sort.RANDOM).limit(1):
                        await self.client.say(post.url)
                elif len(tags) == 5:
                    for post in Search().key(key).query("-grimdark", "-anthro", tags[0], tags[1], tags[2], tags[3], tags[4]).sort_by(sort.RANDOM).limit(1):
                        await self.client.say(post.url)
                            
        else:
            if ctx.message.channel.name != "nsfw":
                for post in Search().query("-explicit", "-grimdark", "-anthro").sort_by(sort.RANDOM).limit(1):
                    await self.client.say(post.url)
            else:
                for post in Search().query("explicit", "-grimdark", "-anthro").sort_by(sort.RANDOM).limit(1):
                    await self.client.say(post.url)
                
def setup(client):
    client.add_cog(search(client))

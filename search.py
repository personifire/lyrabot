import discord
from discord.ext import commands
import derpibooru
from derpibooru import Search, sort

class search:
    def __init__(self, client):
        self.client = client
        self.search = Search(filter_id = 56027) # "everything" filter

    @commands.command(pass_context = True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def search(self, ctx, *args):
        await self.client.send_typing(ctx.message.channel)
        if not (ctx.message.channel.name == "lyra" or ctx.message.channel.name == "test" or ctx.message.channel.name == "nsfw"):
            await self.client.say("<#494919888629006356>")
            return

        if args:
            tags = []
            for tag in args:
                tags.append(tag.replace("_", " "))

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
                if 'anthro' in tags:
                    await self.client.say("You need some better taste!")

                else:   
                    tags.extend(["-explicit", "-grimdark", "-anthro"])
                    for post in self.search.query(*tags).sort_by(sort.RANDOM).limit(1):
                        await self.client.say(post.url)
            else: # in nsfw
                if 'grimdark' in tags or 'anthro' in tags:
                    await self.client.say("<:ew:532536050350948376>")
                else:
                    tags.extend(["-grimdark", "-anthro"])
                    for post in self.search.query(*tags).sort_by(sort.RANDOM).limit(1):
                        await self.client.say(post.url)

        else:
            if ctx.message.channel.name != "nsfw":
                for post in self.search.query("-explicit", "-grimdark", "-anthro").sort_by(sort.RANDOM).limit(1):
                    await self.client.say(post.url)
            else:
                for post in self.search.query("explicit", "-grimdark", "-anthro").sort_by(sort.RANDOM).limit(1):
                    await self.client.say(post.url)

def setup(client):
    client.add_cog(search(client))

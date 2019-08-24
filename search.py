import discord
from discord.ext import commands
import derpibooru
from derpibooru import Search, sort

class search:
    def __init__(self, client):
        self.client = client
        self.searcher = Search(filter_id = 56027) # "everything" filter

    @commands.command(pass_context = True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def search(self, ctx, *args):
        await self.client.send_typing(ctx.message.channel)
        if not (ctx.message.channel.name == "lyra" or ctx.message.channel.name == "test" or ctx.message.channel.name == "nsfw"):
            await self.client.say("<#494919888629006356>")
            return

        tags = []
        joinargs = " ".join(args)
        if "," in joinargs:
            tags = [tag.strip() for tag in joinargs.split(",")]
        else:
            tags = [tag.replace("_", " ") for tag in args]

        if ctx.message.channel.name != "nsfw":
            if 'grimdark' in tags and 'explicit' in tags:
                await self.client.say("Absolutely not.")
            elif 'explicit' in tags or 'questionable' in tags:
                if 'lyra' in tags:
                    await self.client.say("Hey, at least take me out to dinner first!")
                else:
                    await self.client.say("Ponies are NOT for sexual ||at least not in this channel||")
            elif 'grimdark' in tags:
                await self.client.say("I'd rather not see that")
            elif 'anthro' in tags:
                await self.client.say("Get some better taste!")
            else:   
                tags.extend(["-explicit", "-questionable", "-grimdark", "-anthro"])
                for post in self.searcher.query(*tags).sort_by(sort.RANDOM).limit(1):
                    await self.client.say(post.url)
        else: # in nsfw
            if 'grimdark' in tags or 'anthro' in tags:
                await self.client.say("<:ew:532536050350948376>")
            else:
                tags.extend(["-grimdark", "-anthro", "-safe"])
                for post in self.searcher.query(*tags).sort_by(sort.RANDOM).limit(1):
                    await self.client.say(post.url)

def setup(client):
    client.add_cog(search(client))

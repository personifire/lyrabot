import discord
from discord.ext import commands
import derpibooru
from derpibooru import Search, sort

class search(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.searcher = Search(filter_id = 56027) # "everything" filter

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def search(self, ctx, *args):
        if ctx.channel.name == "vchat":
            await ctx.channel.send("<#494919888629006356>")
            return

        tags = []
        joinargs = " ".join(args)
        if "," in joinargs:
            tags = [tag.strip() for tag in joinargs.split(",")]
        else:
            tags = [tag.replace("_", " ") for tag in args]

        if not ctx.channel.is_nsfw():
            if 'grimdark' in tags and 'explicit' in tags:
                await ctx.channel.send("Absolutely not.")
            elif 'explicit' in tags or 'questionable' in tags:
                if 'lyra' in tags:
                    await ctx.channel.send("Hey, at least take me out to dinner first!")
                else:
                    await ctx.channel.send("Ponies are NOT for sexual ||at least not in this channel||")
            elif 'grimdark' in tags:
                await ctx.channel.send("I'd rather not see that")
            elif 'anthro' in tags:
                await ctx.channel.send("Get some better taste!")
            else:   
                tags.extend(["-explicit", "-questionable", "-grimdark", "-anthro"])
                for post in self.searcher.query(*tags).sort_by(sort.RANDOM).limit(1):
                    await ctx.channel.send(post.url)
        else: # in nsfw channel
            if 'grimdark' in tags or 'anthro' in tags:
                await ctx.channel.send("<:ew:532536050350948376>")
            else:
                extratags = ["-grimdark", "-anthro"]
                if 'safe' not in tags:
                    extratags.append("-safe")
                tags.extend(extratags)
            for post in self.searcher.query(*tags).sort_by(sort.RANDOM).limit(1):
                await ctx.channel.send(post.url)

def setup(client):
    client.add_cog(search(client))

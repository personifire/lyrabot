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
        if "_" in joinargs:
            tags = [tag.replace("_", " ") for tag in args]
        else:
            tags = [tag.strip() for tag in joinargs.split(",")]

        # meme joke
        youremom = ["you're mom", "youre mom", "you'remom", "youremom"]
        for mom in youremom:
            try:
                index = tags.index(mom)
                tags[index] = "gay"
            except ValueError:
                pass

        results = None

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
                results = self.searcher.query(*tags).sort_by(sort.RANDOM).limit(1)
        else: # in nsfw channel
            if 'grimdark' in tags or 'anthro' in tags:
                await ctx.channel.send("<:ew:532536050350948376>")
            else:
                extratags = ["-grimdark", "-anthro"]
                if 'safe' not in tags:
                    extratags.append("-safe")
                tags.extend(extratags)
            results = self.searcher.query(*tags).sort_by(sort.RANDOM).limit(1)
        if results is not None:
            posted = False
            for post in results:
                await ctx.channel.send(post.url)
                posted = True
            if not posted:
                await ctx.channel.send('No results for search "' + joinargs + '". Too niche!')

def setup(client):
    client.add_cog(search(client))

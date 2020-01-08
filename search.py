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
        tags = []
        joinargs = " ".join(args)
        if "_" in joinargs:
            joinargs = joinargs.replace(" ", ",")
            joinargs = joinargs.replace("_", " ")
        tags = list(filter(None, [tag.strip() for tag in joinargs.split(",")]))

        # meme joke
        youremom = ["you're mom", "youre mom", "you'remom", "youremom"]
        for mom in youremom:
            try:
                index = tags.index(mom)
                tags[index] = "gay"
            except ValueError:
                pass

        results = None

        # validate and choose content filtering tags
        extratags = []
        if not ctx.channel.is_nsfw():
            if 'grimdark' in tags and 'explicit' in tags:
                await ctx.channel.send("Absolutely not.")
                return
            elif 'explicit' in tags or 'questionable' in tags or 'suggestive' in tags:
                if 'lyra' in tags:
                    await ctx.channel.send("Hey, at least take me out to dinner first!")
                else:
                    await ctx.channel.send("Ponies are NOT for sexual ||at least not in this channel||")
                return
            elif 'grimdark' in tags:
                await ctx.channel.send("I'd rather not see that")
                return
            elif 'anthro' in tags:
                await ctx.channel.send("Get some better taste!")
                return

            extratags = ["-explicit", "-questionable", "-suggestive", "-grimdark", "-anthro"]
        else: # in nsfw channel
            if 'grimdark' in tags or 'anthro' in tags:
                await ctx.channel.send("<:ew:532536050350948376>")
                return
            else:
                extratags = ["-grimdark", "-anthro"]
                if 'safe' not in tags:
                    extratags.append("-safe")
                tags.extend(extratags)

        for attempt in range(2):
            results = self.searcher.query(*(tags + extratags)).sort_by(sort.RANDOM).limit(1)

            if results is not None:
                posted = False                         # ugly workaround because results doesn't say if there's anything inside unless you look
                for post in results:
                    await ctx.channel.send(post.url)
                    posted = True
                if posted:
                    break

            # first attempt didn't work, try splitting on spaces
            tags = " ".join(tags).split(" ")

        if not posted:
            await ctx.channel.send('No results for search "' + joinargs + '". Too niche!')

def setup(client):
    client.add_cog(search(client))

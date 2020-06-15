import discord
from discord.ext import commands
import derpibooru
from derpibooru import Search, sort

import re
import requests

class search(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.searcher = Search(filter_id = 56027) # "everything" filter


    def get_derpi_embed(self, image_id, image_url, oembed):
        url = f'https://derpibooru.org/images/{image_id}'
        title = oembed["title"]
        if len(title) > 70:
            title = f'{title[:67]}...'
        embed = discord.Embed(
                title = title,
                url = url,
                color = 6393795
        ).set_author(name = oembed["author_name"]
        ).set_image(url = image_url)
        return embed

    async def do_sfw_snark(self, ctx, tags):
        if 'grimdark' in tags and 'explicit' in tags:
            await ctx.channel.send("Absolutely not.")
        elif 'explicit' in tags or 'questionable' in tags or 'suggestive' in tags:
            if 'lyra' in tags:
                await ctx.channel.send("Hey, at least take me out to dinner first!")
            else:
                await ctx.channel.send("Ponies are NOT for sexual ||at least not in this channel||")
        elif 'grimdark' in tags:
            await ctx.channel.send("I'd rather not see that")
        elif 'anthro' in tags:
            await ctx.channel.send("Get some better taste!")
        else:
            return False
        return True


    async def do_nsfw_snark(self, ctx, tags):
        if 'grimdark' in tags or 'anthro' in tags:
            await ctx.channel.send("<:ew:532536050350948376>")
            return True
        return False


    async def do_escape_paren_snark(self, ctx, tags):
        searchstring = ", ".join(tags)

        quoted  = False
        escaped = False
        balance = 0
        for char in searchstring:
            if quoted:
                if char == "\"":
                    quoted = False
                continue
            elif char == "\"":
                quoted = True
                continue

            if escaped:
                escaped = False
                continue
            elif char == "\\":
                escaped = True
                continue

            if char == "(":
                balance += 1
            elif char == ")":
                balance -= 1

            if balance < 0:
                await ctx.channel.send("Very funny.")
                return True
        return False


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        regex = re.compile("derpicdn.net")
        for embed in message.embeds:
            thumb = embed.thumbnail
            if thumb == discord.Embed.Empty:
                thumb = embed.image
                if thumb == discord.Embed.Empty:
                    continue

            if regex.search(thumb.url):
                oembed_url = f'https://derpibooru.org/api/v1/json/oembed?url={thumb.url}'
                data = requests.get(oembed_url).json()
                if data["author_url"] is not None:
                    return

                image_id = data["derpibooru_id"]
                idata = requests.get(f'https://derpibooru.org/api/v1/json/images/{image_id}').json()
                while "duplicate_of" in idata:
                    image_id = idata["image"]["duplicate_of"]
                    idata = requests.get(f'https://derpibooru.org/api/v1/json/images/{image_id}').json()

                image_url = idata["image"]["representations"]["full"]
                await message.channel.send(embed = self.get_derpi_embed(image_id, image_url, data))


    @commands.command(aliases=["rollzig"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rollzigger(self, ctx):
        """ Posts a random zigzog """
        await self.search(ctx, args = "Zecora")


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def search(self, ctx, *, args = "*"):
        """ Searches derpibooru for a given set of tags """
        tags = []
        if "_" in args:
            args = args.replace(" ", ",")
            args = args.replace("_", " ")
        tags = list(filter(None, [tag.strip() for tag in args.split(",")]))

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
        if await self.do_escape_paren_snark(ctx, tags):
            return

        extratags = []
        if (not ctx.channel.type == discord.ChannelType.private 
            and not ctx.channel.type == discord.ChannelType.group
            and not ctx.channel.is_nsfw()):
            if await self.do_sfw_snark(ctx, tags):
                return
            extratags = ["-explicit", "-questionable", "-suggestive", "-grimdark", "-anthro"]
        else: # in nsfw channel
            if await self.do_nsfw_snark(ctx, tags):
                return
            else:
                extratags = ["-grimdark", "-anthro"]

        for attempt in range(2):
            results = self.searcher.query(*extratags, "(" + ", ".join(tags) + ")").sort_by(sort.RANDOM).limit(1)

            if results is not None:
                posted = False                         # ugly workaround because results doesn't say if there's anything inside unless you look
                for post in results:
                    oembed_url = f'https://derpibooru.org/api/v1/json/oembed?url=https://derpibooru.org/{post.id}'
                    data = requests.get(oembed_url).json()
                    if data["author_url"] is not None:
                        await ctx.send(post.url)
                    else:
                        await ctx.send(embed=self.get_derpi_embed(post.id, post.full, data))
                    posted = True
                if posted:
                    break

            # first attempt didn't work, try splitting on spaces
            tags = " ".join(tags).split(" ")

        if not posted:
            await ctx.channel.send('No results for search "' + args + '". Too niche!')

def setup(client):
    client.add_cog(search(client))

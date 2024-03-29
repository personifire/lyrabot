import discord
from discord.ext import commands

import asyncio
import aiohttp

class search(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.client.loop.create_task(self.session.close()) # failure and exact time don't really matter


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


    @commands.command(aliases=["rollzig"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rollzigger(self, ctx):
        """ Posts a random zigzog """
        await self.search(ctx, args = "Zecora")


    def get_url_from_message(self, msg):
        # trying to reverse search more than one image is for nerds
        if len(msg.embeds) > 0:
            for embed in msg.embeds:
                if embed.thumbnail is not None and embed.thumbnail.url is not None:
                    return embed.thumbnail.url
                if embed.image is not None and embed.image.url is not None:
                    return embed.image.url
        elif len(msg.attachments) > 0:
            valid_image_content_types = [
                    "image/jpg",     "image/jpeg",
                    "image/png",     "image/gif",
                    "image/svg+xml", "video/webm",
            ]
            for attachment in msg.attachments:
                if attachment.content_type in valid_image_content_types:
                    return attachment.url

        return None

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reverse(self, ctx, url = None, distance = None):
        """ Reverse searches an image on derpibooru

        Can take an image URL. Will look for an image in a replied-to message, if given, or the last five messages in the channel if not.
        Can also take a "match distance" -- defaults to 0.25, should probably be 0.2-0.5 in general.
        """
        # check if url is actually "match distance"
        if distance is None:
            try:
                distance = float(url)
                url = None
            except (ValueError, TypeError): # url is actually a url, or is None
                pass

        if url is None:
            if ctx.message.reference is not None:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                url = self.get_url_from_message(msg)
        if url is None:
            async for msg in ctx.channel.history(limit = 5):
                url = self.get_url_from_message(msg)
                if url is not None:
                    break

        if url is None:
            await ctx.reply("Couldn't find an image to reverse search!")

        params = { 'url': url }
        if distance is not None:
            params['distance'] = distance
        reverse_url = "https://derpibooru.org/api/v1/json/search/reverse"
        async with self.session.post(reverse_url, params = params) as reverse:
            if reverse.ok:
                images = (await reverse.json())["images"]
                if len(images) == 0:
                    await ctx.reply("Doesn't look like derpi has it, sorry.")
                else: # maybe one day menus will be released and you can have a reasonable interface to show multiple results
                    await ctx.reply(f"https://derpibooru.org/{images[0]['id']}")
            else:
                await ctx.reply("Uhh, sorry. Try again?")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def search(self, ctx, *, args = "*"):
        """ Searches derpibooru for a given set of tags """
        tags = []
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

        search_url = "https://derpibooru.org/api/v1/json/search/images"
        for attempt in range(2):
            params = { 
                    'q': f"{', '.join(extratags)}, ({', '.join(tags)})",
                    'sf': 'random',
                    'per_page': 1,
            }
            async with self.session.get(search_url, params = params) as search:
                if search.ok:
                    images = (await search.json())["images"]
                    if len(images) > 0:
                        return await ctx.send(f"https://derpibooru.org/{images[0]['id']}")
                else:
                    return await ctx.send(f"Uh... Whoops! ({search.status}). Try again?")

            # first attempt didn't work, try the dumb underscore/space thing
            tags = ",".join(tags).replace(" ", ",").replace("_", " ").split(",")

        # neither attempt worked, rip
        return await ctx.channel.send('No results for search "' + args + '". Too niche!')


async def setup(client):
    await client.add_cog(search(client))

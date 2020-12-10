import discord
from discord.ext import commands
import os
import typing

import lib.hat

class image(commands.Cog):
    """ Does various image things (eventually) """
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["santa"])
    @commands.max_concurrency(1, wait=True)
    async def santahat(self, ctx, image:typing.Union[discord.Member, str] = None):
        """ Get into the holiday cheer!

        Will take a image URL, user mention, attachment, or just your avatar
        """
        # set arg appropriately
        if isinstance(image, discord.Member):
            image = str(image.avatar_url)
        elif image is None:
            if len(ctx.message.attachments) > 0:
                image = ctx.message.attachments[0].url
            else:
                image = str(ctx.author.avatar_url)

        img_outname = image.split('/')[-1].split('?')[0].split('#')[0] # this is kind of dumb tbqh
        img_outname = f'data/{img_outname}'

        async with ctx.typing():
            result = await self.client.loop.run_in_executor(None, lib.hat.enhat_image, image, img_outname)
            if result is None:
                await ctx.send("Doesn't look like an image to me!")
            elif isinstance(result, str):
                print(result)
                await ctx.send('What\'s a "geef"?')
            elif result:
                await ctx.send(file=discord.File(img_outname))
            else:
                await ctx.send("Well, I tried my best...", file=discord.File(img_outname))

        os.remove(img_outname)

def setup(client):
    client.add_cog(image(client))

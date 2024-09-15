import importlib
import os
import typing

import lib.hat

import discord
from discord.ext import commands

class image(commands.Cog):
    """ Does various image things (eventually) """
    def __init__(self, client):
        self.client = client
        self.num_files = 0

    def reserve_imgname(self, img_name):
        output_name = f"data/{img_name}"
        counter = 0
        while os.path.isfile(output_name):
            output_name = f"data/{counter}_{img_name}"
            counter += 1
        open(output_name, 'a').close()
        return output_name


    @commands.command(aliases=["santa"])
    @commands.max_concurrency(5, wait=True)
    async def santahat(self, ctx, image:typing.Union[discord.Member, str] = None):
        """ Get into the holiday cheer!

        Will take a image URL, user mention, attachment (possibly in reply), or just your avatar
        """
        # set arg appropriately
        if isinstance(image, discord.Member):
            image = str(image.display_avatar)
        elif image is None:
            if len(ctx.message.attachments) > 0:
                image = ctx.message.attachments[0].url
            elif ctx.message.reference is not None:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                if len(msg.attachments) > 0:
                    image = msg.attachments[0].url
            else:
                image = str(ctx.author.display_avatar)

        img_outname = image.split('/')[-1].split('?')[0].split('#')[0] # this is kind of dumb tbqh
        root, ext = os.path.splitext(img_outname)
        if ext.lower() == ".gif":
            # hatten() uses cv2.imwrite, which doesn't support writing GIFs. Pillow does,
            # but we might as well use PNG since it isn't limited to 256 colors.
            img_outname = root + ".png"
        img_outname = self.reserve_imgname(img_outname)

        async with ctx.typing():
            result = await self.client.loop.run_in_executor(None, lib.hat.enhat_image, image, img_outname)
            if result is None:
                return await ctx.send("Doesn't look like an image to me!")
            elif isinstance(result, str):
                print(result)
                return await ctx.send('What\'s a "geef"?')
            elif result:
                await ctx.send(file=discord.File(img_outname))
            else:
                await ctx.send("Well, I tried my best...", file=discord.File(img_outname))

        os.remove(img_outname)

    @commands.command()
    @commands.max_concurrency(5, wait=True)
    async def heard(self, ctx, image:typing.Union[discord.Member, str] = None):
        """ Get up, get down if you're gonna come around...

        Will take a image URL, user mention, attachment (possibly in reply), or just your avatar
        """
        # set arg appropriately
        if isinstance(image, discord.Member):
            image = str(image.display_avatar)
        elif image is None:
            if len(ctx.message.attachments) > 0:
                image = ctx.message.attachments[0].url
            elif ctx.message.reference is not None:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                if len(msg.attachments) > 0:
                    image = msg.attachments[0].url
            else:
                image = str(ctx.author.display_avatar)

        img_outname = image.split('/')[-1].split('?')[0].split('#')[0] # this is kind of dumb tbqh
        root, ext = os.path.splitext(img_outname)
        if ext.lower() == ".gif":
            # hatten() uses cv2.imwrite, which doesn't support writing GIFs. Pillow does,
            # but we might as well use PNG since it isn't limited to 256 colors.
            img_outname = root + ".png"
        img_outname = self.reserve_imgname(img_outname)

        async with ctx.typing():
            result = await self.client.loop.run_in_executor(None, 
                lib.hat.enhat_image, image, img_outname, 'heard/ears'
            )
            if result is None:
                return await ctx.send("Doesn't look like an image to me!")
            elif isinstance(result, str):
                print(result)
                return await ctx.send('What\'s a "geef"?')
            elif result:
                await ctx.send(file=discord.File(img_outname))
            else:
                await ctx.send("Well, I tried my best...", file=discord.File(img_outname))

        os.remove(img_outname)


    def cog_unload(self):
        importlib.reload(lib.hat)

async def setup(client):
    await client.add_cog(image(client))

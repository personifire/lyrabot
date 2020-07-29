import asyncio

import discord
from discord.ext import commands

async def ffmpeg_run(*args):
    cmd = "ffmpeg"

    process = await asyncio.create_subprocess_exec(cmd, *args)
    return_value = await process.wait()

    return return_value

class video(commands.Cog):
    """ Does various video things """
    def __init__(self, client):
        self.client = client

    @commands.command()
    #async def stickbug(self, ctx, duration1, duration2 = 10, video = None):
    async def stickbug(self, ctx, duration1, video = None):
        if video is None:
            return # TODO check for last posted video embed/upload

        try:
            duration1 = float(duration1)
        except ValueError:
            await ctx.send("That's not a valid duration!")
            return

        duration2 = 10

        # automatically say yes to overwrite, trim duration of inputs
        args  = f'-y -t {duration1} -i {video} -t {duration2} -i files/stickbug.mp4 -filter_complex'.split(" ")
        # scale to minimum that fits 1280x720 (resolution of the stickbug video)
        filters  = '[0:v] scale=iw*min(1280/iw\,720/ih):ih*min(1280/iw\,720/ih), '
        # pad to fit
        filters += 'pad=w=1280:h=720:x=(ow-iw)/2:y=(oh-ih)/2 [padvid], '
        # cat the videos
        filters += '[padvid] [0:a] [1:v] [1:a] concat=n=2:v=1:a=1 [v] [a]'
        args += [filters]
        # only include the final video/audio streams in output
        args += '-map [v] -map [a] data/stickbug.mp4'.split(" ")

        #args = args.split(" ")
        print(f"Sending these args: {args}")
        async with ctx.typing():
            await ffmpeg_run(*args)
            await ctx.send(file=discord.File('data/stickbug.mp4'))

def setup(client):
    client.add_cog(video(client))

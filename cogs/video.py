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

        # trim duration 
        args  = f' -t {duration1} -i {video} -t {duration2} -i files/stickbug.mp4 -filter_complex "'
        # scale to minimum that fits 1280x720 (resolution of the stickbug video) (implicitly send output to next stage)
        args += ' [0:v] scale=iw*min(1280/iw\,720/ih):ih*min(1280/iw\,720/ih), '
        # pad to fit (name video output stream "padvid") (comma means same "linear chain", semicolon would mean not same)
        args += ' pad=w=1280:h=720 [padvid], '
        # cat the videos
        args += ' [padvid] [0:a] [1:v] [1:a] concat=n=2:v=1:a=1 [v] [a]" '
        # only include the final video/audio streams in output
        args += ' -map "[v]" -map "[a]" data/stickbug.mp4'

        print(f"Sending these args: {args}")
        async with ctx.typing():
            await ffmpeg_run(args)
            await ctx.send(file=discord.File('data/stickbug.mp4'))

def setup(client):
    client.add_cog(video(client))

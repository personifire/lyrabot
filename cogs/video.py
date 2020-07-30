import asyncio

import discord
from discord.ext import commands

async def ffmpeg_run(*args):
    cmd = "ffmpeg"

    process = await asyncio.create_subprocess_exec(cmd, *args)
    return_value = await process.wait()

    return return_value

async def stickbugify(duration, video):
        # automatically say yes to overwrite, trim duration of inputs
        args  = f'-y -t {duration} -i {video} -t 10 -i files/stickbug.mp4 -filter_complex'.split(" ")
        # scale to minimum that fits 1280x720 (resolution of the stickbug video)
        filters  = '[0:v] scale=iw*min(1280/iw\,720/ih):ih*min(1280/iw\,720/ih), '
        # pad to fit
        filters += 'pad=w=1280:h=720:x=(ow-iw)/2:y=(oh-ih)/2 [padvid], '
        # cat the videos
        filters += '[padvid] [0:a] [1:v] [1:a] concat=n=2:v=1:a=1 [v] [a]'
        args += [filters]
        # only include the final video/audio streams in output
        args += '-map [v] -map [a] data/stickbug.mp4'.split(" ")

        return await ffmpeg_run(*args)

class video(commands.Cog):
    """ Does various video things """
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.max_concurrency(1, wait=True)
    async def stickbug(self, ctx, delay = None, video = None):
        """ Does the ebin stickbug meme

        Can take a video URL, attachment, or embed -- will look in the past five messages if not found.
        Can also take a custom length for the first video to play!
        """
        # determine arity and set args appropriately
        try:
            delay = float(delay)
            if (delay > 30.0 or delay < 0) and not self.client.is_owner(ctx.author):
                return await ctx.send("That sure is a neat length there!")
        except (ValueError, TypeError): # delay is actually video, or is None
            video = delay
            delay = 0.5

        if video is None:
            async for vidmsg in ctx.channel.history(limit = 5):
                if len(vidmsg.attachments) > 0:
                    video = vidmsg.attachments[0].url
                    break
                elif len(vidmsg.embeds) > 0 and vidmsg.embeds[0].video.url is not discord.Embed.Empty:
                    video = vidmsg.embeds[0].video.url
                    break
            if video is None:
                return await ctx.send("Is there a video to stickbug?")

        async with ctx.typing():
            if not await stickbugify(delay, video):
                await ctx.send(file=discord.File('data/stickbug.mp4'))
            else:
                await ctx.send("Sorry, stickbug just ain't feeling it today!")

def setup(client):
    client.add_cog(video(client))

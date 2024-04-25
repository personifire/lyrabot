import asyncio
import io
import importlib
import json
import subprocess
import sys

import discord
from discord.ext import commands
import discord.errors

ytdl_format_options = {
    'format': 'bestaudio/best',
    'buffer-size': 4096,
    'output': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrict-filenames': True,
    'no-playlist': True,
    'no-check-certificate': True,
    'ignore-errors': False,
    'quiet': True,
    'no-warnings': True,
    'default-search': 'ytsearch',
    'source-address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class YTDLException(Exception):
    pass

class EspeakException(Exception):
    pass

async def ytdl_get_data(url):
    exe  = "yt-dlp"
    args = ["-J"] # to call yt-dlp and dump info as a single line of JSON

    for flag, value in ytdl_format_options.items():
        if value is False:
            continue

        args.append(f"--{flag}" if len(flag) > 1  else f"-{flag}")

        # binary flags don't take an arg
        if not isinstance(value, bool):
            args.append(str(value))

    args.append(url)

    ytdl_process = await asyncio.create_subprocess_exec(exe, *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = await ytdl_process.communicate()
    if ytdl_process.returncode != 0:
        raise YTDLException(stderr) # :)

    return json.loads(stdout.decode("utf-8"))

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, title, url, volume=0.25):
        super().__init__(source, volume)

        self.title = title
        self.url = url


    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        # TODO something when the "stream" arg is false, probably
        data = await ytdl_get_data(url)

        if 'entries' in data:
            # take first item from a playlist
            # TODO look at playlist support
            data = data['entries'][0]

        title = data.get('title')
        url   = data['url']

        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), title=title, url=url)

async def espeak_source(*text):
    cmd = "espeak"

    process = await asyncio.create_subprocess_exec(cmd, *text, "--stdout", stdout=subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return discord.FFmpegPCMAudio(io.BytesIO(stdout), options = ffmpeg_options['options'], pipe=True)



# TODO allow two audio streams to be combined on-the-fly -- consider possibilities:
#  1. source A plays out beginning to end
#  2. source A plays, then source B starts in the middle, and:
#    a. source A ends first
#    b. source B ends first
#    c. the two sources end simultaneously
#  3. source A plays, then source B starts in the middle, then source A ends, then source C is queued


# manage a voice connection with associated queue
# may die unexpectedly if disconnected from vc and reconnection times out
class VoiceQueuedPlayerClient(discord.VoiceClient):
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        super().__init__(client, channel)

        self.queued_players = []
        self._play_next = asyncio.Event()
        self._play_loop = asyncio.create_task(self._queue_loop())

    async def disconnect(self, *, force=False):
        await super().disconnect(force=force)

    def cleanup(self):
        super().cleanup()
        if not self._play_loop.done():
            self._play_loop.cancel()

    def queue(self, player):
        self.queued_players.append(player)
        if len(self.queued_players) == 1 and not self.is_playing() and not self.is_paused():
            self._play_next.set()

    def skip(self, index=0):
        """ skip a player; returns title of skipped player if successful, or False otherwise. """
        if index == 0 and self.source:
            title = self.source.title
            self.stop()
        elif index > 0 and len(self.queued_players) >= index:
            title = self.queued_players[index - 1].title
            del self.queued_players[index - 1]
        else:
            return False
        return title

    def get_queue_titles(self):
        titles = [player.title for player in self.queued_players]
        if self.source:
            return [self.source.title, *titles]
        else:
            return titles

    async def _queue_loop(self):
        try:
            max_idle_time = 3600 # one hour timeout

            while await asyncio.wait_for(self._play_next.wait(), max_idle_time):
                self._play_next.clear()

                if len(self.queued_players) > 0:
                    player = self.queued_players.pop(0)
                    self.play(player, after=self._set_next)
                    self.playing = player.title
                else:
                    self.playing = None
        except asyncio.CancelledError:
            pass
        except TimeoutError:
            pass # timed out a long time without playing audio
        finally:
            await self.disconnect()

    def _set_next(self, err=None):
        self._play_next.set()

        if err:
            raise err # look, I dunno what to do with it



class vchat(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def _join_channel(self, guild, voice_channel):
        vclient = guild.voice_client
        if vclient is None or not vclient.is_connected():
            vclient = await voice_channel.connect(cls=VoiceQueuedPlayerClient)
        elif vclient.channel != voice_channel:
            await vclient.move_to(voice_channel)

        return vclient

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() == "gay chat" and message.channel.name.lower() == "vchat":
            for vc in message.guild.voice_channels:
                if len(vc.members) > 0:
                    vclient = await self._join_channel(message.guild, vc)

                    player = discord.FFmpegPCMAudio("files/urmom.mp3", options = ffmpeg_options['options'])
                    player.title = "you're mom gay"

                    vclient.queue(player)
                    return


    @commands.command(aliases = ["update_ytdlp"])
    @commands.is_owner()
    async def update_youtubedl(self, ctx):
        """ Update the yt-dlp module in hopes that it fixes things """
        args = ["-m", "pip", "install", "--upgrade", "yt-dlp"]
        process = await asyncio.create_subprocess_exec(sys.executable, *args)
        await process.wait()

        await ctx.send("Well, try it out!")


    @commands.command()
    async def vtts(self, ctx, *, txt):
        if ctx.author.voice and ctx.author.voice.channel:
            vclient = await self._join_channel(ctx.guild, ctx.author.voice.channel)

        if ctx.guild.voice_client is None:
            return await ctx.send("You're not in vchat!")

        player = await espeak_source(txt)
        player.title = f"tts: {txt}"

        vclient.queue(player)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        vchannel = before.channel
        if vchannel and not after.channel and vchannel.guild.voice_client:
            vclient = vchannel.guild.voice_client
            my_channel = vclient.channel
            if vchannel != my_channel and all(member.bot for member in my_channel.members):
                await vclient.disconnect()


    async def cog_unload(self):
        # nobody else is gonna be handling voice clients, get rid of 'em
        for vclient in self.client.voice_clients:
            await vclient.disconnect()


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def join(self, ctx):
        """ Joins the user's voice channel """
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            await self._join_channel(ctx.guild, ctx.author.voice.channel)
        else:
            await ctx.channel.send("*shrugs*")


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def leave(self, ctx):
        """ Leaves the voice channel """
        vclient = ctx.voice_client
        if vclient:
            await vclient.disconnect()
            await ctx.channel.send("Later!")
        else:
            await ctx.channel.send("I'm not even in a voice channel though...")


    @commands.command(aliases = ["play"])
    async def vplay(self, ctx, *search):
        """ Plays or queues audio from the url or search term """
        if ctx.author.voice and ctx.author.voice.channel:
            vclient = await self._join_channel(ctx.guild, ctx.author.voice.channel)
        else:
            return await ctx.channel.send("You're not in a voice channel! *shrugs*")

        url = " ".join(search)

        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(url, loop=self.client.loop)
            except YTDLException as err:
                if ctx.channel.permissions_for(ctx.me).send_messages:
                    await ctx.send("Something bad happened while I was looking for that, sorry!")
                raise err

            vclient.queue(player)
            await ctx.channel.send("Gotcha, queueing " + player.title + ", " + ctx.author.name)


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def pause(self, ctx):
        """ Pauses playback of the current audio """
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.channel.send("Can't pause if a song isn't playing!")


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def resume(self, ctx):
        """ Resumes playback of the current audio """
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        else:
            await ctx.channel.send("Can't resume if a song isn't paused!")


    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def skip(self, ctx, index = 0):
        """ Skips the current song

        if no number is provided, ends playback of the current audio
        """
        vclient = ctx.voice_client
        if vclient is None:
            return await ctx.channel.send("lol good one")

        skipped = vclient.skip(index)
        if skipped:
            if index == 0:
                index = "current song"
            await ctx.channel.send(f"Skipping {index}: {skipped}")
        else:
            await ctx.channel.send("Y'know, I'm not really sure what that number means...")


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def queue(self, ctx):
        """ Displays the audio currently in the queue """
        vclient = ctx.voice_client
        if vclient:
            queue = vclient.get_queue_titles()
        else:
            return await ctx.channel.send("Am I even in vchat?")

        if len(queue) > 0:
            output = f"Currently playing: {queue[0]}\n"
            for index, title in enumerate(queue[1:]):
                output += f"{index + 1}: {title}\n"
        else:
            output = "No songs in queue"

        await ctx.channel.send(output)


    @commands.command()
    @commands.bot_has_guild_permissions(move_members = True)
    async def yeet(self, ctx, mention:discord.Member = None):
        if mention is not None and ctx.author.guild_permissions.move_members:
            victim = mention
        else:
            victim = ctx.author
        if victim.voice and victim.voice.channel:
            await victim.move_to(None, reason="YEET")



async def setup(client):
    await client.add_cog(vchat(client))

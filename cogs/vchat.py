import asyncio
import audioop
from io import BytesIO
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

class PCMMixerException(Exception):
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

async def ytdl_source(url):
    data = await ytdl_get_data(url)

    if 'entries' in data:
        # take first item from a playlist
        data = data['entries'][0]

    title = data.get('title')
    url   = data['url']

    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpeg_options))
    source.title = title
    return source

async def espeak_source(text):
    cmd = "espeak"

    process = await asyncio.create_subprocess_exec(cmd, text, "--stdout", stdout=subprocess.PIPE)
    stdout, stderr = await process.communicate()

    source = discord.FFmpegPCMAudio(BytesIO(stdout), options = ffmpeg_options['options'], pipe=True)
    max_title_len = 25
    if len(text) > max_title_len:
        text = f"{text[:max_title_len-3]}..."
    source.title = f"tts({text})"
    return source



class PCMMixerTransformer(discord.AudioSource):
    """ Transformer that mixes audio between multiple sources. 

    Eagerly gets rid of sub-sources when done, including other mixed Transformers. 
    This may cause unexpected changes to Transformer objects; be warned.
    """
    def __init__(self, *sources, title=None):
        if len(sources) == 0:
            raise PCMMixerException("Initialized with no sources!")
        for source in sources:
            if source.is_opus():
                raise PCMMixerException(f"Got opus-encoded source!")

        self.done = False
        self.sources = list(sources)

    @property
    def title(self):
        if len(self.sources) > 0:
            return [source.title for source in self.sources]
        else:
            return None

    def mix(self, source):
        if self.done:
            raise PCMMixerException("Got new source when already done!")
        if source.is_opus():
            raise PCMMixerException(f"Got opus-encoded source!")
        self.sources.append(source)

    def unmix(self, index=0):
        if self.done:
            raise PCMMixerException("Unmixed after done!")
        if len(self.sources) <= index:
            raise PCMMixerException("Skip indexed past end!")
        source = self.sources.pop(index)
        if len(self.sources) == 0:
            self.done = True
        return source

    def read(self):
        """ reads from sub-sources; removes ones that are done. 

        Will be called from a separate thread in order to play audio. """
        to_remove = []
        buf = None
        for idx, source in enumerate(self.sources):
            mix = source.read()
            if len(mix) == 0:
                to_remove.append(idx)
            elif buf is not None:
                buf = audioop.add(buf, mix, 2)
            else:
                buf = mix

        for idx in reversed(to_remove):
            del self.sources[idx]

        if buf is None:
            self.done = True
            return b""
        return buf



class VoiceQueuedPlayerClient(discord.VoiceClient):
    """ Manage a voice connection with associated queue """
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        super().__init__(client, channel)

        self.queued_sources = []
        self.mixed_source = None
        self._play_done = asyncio.Event()
        self._play_loop = asyncio.create_task(self._queue_loop())

    def cleanup(self):
        super().cleanup()
        if not self._play_loop.done():
            self._play_loop.cancel()

    def queue(self, source):
        self.queued_sources.append(source)
        if len(self.queued_sources) == 1 and not self.is_playing() and not self.is_paused():
            self._play_done.set()

    def queue_mixed(self, source):
        is_paused = self.is_paused()
        self.pause()
        if self.mixed_source and not self.mixed_source.done:
            self.mixed_source.mix(source)
        else:
            self.mixed_source = PCMMixerTransformer(source)
            if self.is_playing():
                if isinstance(self.source, PCMMixerTransformer):
                    self.source.mix(self.mixed_source)
                else:
                    self.source = PCMMixerTransformer(self.source, self.mixed_source)
            elif not self.is_paused():
                self._play_done.set()
        if not is_paused:
            self.resume()

    def skip(self, index=0):
        """ skip a source; returns title of skipped source if successful, or False otherwise. """
        if index == 0 and self.source:
            title = self.source.title
            self.stop()
            return title
        elif index > 0 and len(self.queued_sources) >= index:
            title = self.queued_sources[index - 1].title
            del self.queued_sources[index - 1]
            return title
        elif isinstance(index, str) and index.isalpha():
            index = ord(index) - ord("A")
            # this may be broken but I'm not gonna fix it until somebody tells me so:
            if index > 0 and len(self.mixed_source.sources) >= index:
                return self.mixed_source.unmix(index).title
        return False

    def get_queue_titles(self):
        titles = [source.title for source in self.queued_sources]
        if self.source:
            return [self.source.title, *titles]
        else:
            return titles

    async def _queue_loop(self):
        try:
            max_idle_time = 3600 # one hour timeout

            while await asyncio.wait_for(self._play_done.wait(), max_idle_time):
                self._play_done.clear()

                # get next source, if any
                if len(self.queued_sources) > 0:
                    source = self.queued_sources.pop(0)
                elif self.mixed_source:
                    source = self.mixed_source.unmix()
                else:
                    continue

                # mix sources if required
                if self.mixed_source:
                    if self.mixed_source.done:
                        self.mixed_source = None
                    elif isinstance(source, PCMMixerTransformer):
                        source.mix(self.mixed_source)
                    else:
                        source = PCMMixerTransformer(source, self.mixed_source)

                # play audio
                self.play(source, after=self._play_next)
        except asyncio.CancelledError:
            pass
        except TimeoutError:
            pass # timed out a long time without playing audio
        finally:
            await self.disconnect()

    def _play_next(self, err=None):
        self._play_done.set()

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

                    source = discord.FFmpegPCMAudio("files/urmom.mp3", options = ffmpeg_options['options'])
                    source.title = "you're mom gay"

                    vclient.queue(source)
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
            return await ctx.channel.send("You're not in a voice channel! *shrugs*")

        source = await espeak_source(txt)

        vclient.queue_mixed(source)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        vchannel = before.channel
        if vchannel and not after.channel and vchannel.guild.voice_client:
            vclient = vchannel.guild.voice_client
            my_channel = vclient.channel
            if vchannel == my_channel and all(member.bot for member in my_channel.members):
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
            await ctx.channel.send("You're not in a voice channel! *shrugs*")


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
                source = await ytdl_source(url)
            except YTDLException as err:
                if ctx.channel.permissions_for(ctx.me).send_messages:
                    await ctx.send("Something bad happened while I was looking for that, sorry!")
                raise err

            if ctx.command == self.vplay:
                vclient.queue(source)
            else: # vplay_mixed
                vclient.queue_mixed(source)
            await ctx.channel.send("Gotcha, queueing " + source.title + ", " + ctx.author.name)

    @commands.command(aliases = ["vmix", "vmash"])
    async def vplay_mixed(self, ctx, *search):
        """ Plays audio simultaneously to other audio, from the url or search term

        This gets silly rather quickly. Behavior may be slightly broken.
        """
        await self.vplay(ctx, *search)


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
        elif skipped is not None: # None means no title; does not mean nothing was skipped
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
            if isinstance(queue[0], list):
                # depth-first search for titles
                to_visit = list(reversed(queue[0]))
                visited = []
                while len(to_visit) > 0:
                    curr = to_visit.pop()
                    if isinstance(curr, list):
                        to_visit.extend(reversed(curr))
                    else:
                        visited.append(curr)

                output = f"Currently playing: {visited[0]}\n"
                offset = ord("A")
                for index, title in enumerate(visited[1:]):
                    output += f"; {chr(index + offset)}: {title}"
            else:
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

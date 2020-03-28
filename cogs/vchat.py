import discord
from discord.ext import commands
import discord.errors
import youtube_dl

ytdl_format_options = {
    'format': 'bestaudio/best',
    'buffersize': 4096,
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.25):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            # TODO look at playlist support
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class vchat(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() == "gay chat" and message.channel.name.lower() == "vchat":
            for vc in message.guild.voice_channels:
                if len(vc.members) > 0:
                    voice_client = message.guild.voice_client
                    await self.join_channel(voice_client, vc)
                    voice_client = message.guild.voice_client

                    player = discord.FFmpegPCMAudio("files/urmom.mp3", **ffmpeg_options)
                    player.title = "you're mom gay"

                    self.queue[message.guild.id].append(player)
                    if not voice_client.is_playing() and not voice_client.is_paused():
                        print("Nothing was in queue when " + player.title + " was queued")
                        self.play_next(message)
                    return

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def vchat(self, ctx):
        """ Outputs some custom help """
        output =  "```"
        output += "!join                  Joins the user's voice channel\n"
        output += "!leave                 Leaves the voice channel\n"
        output += "!play [url | search]   Plays or queues audio from the url or search term\n"
        output += "!pause                 Pauses playback of the current audio\n"
        output += "!resume                Resumes playback of the current audio\n"
        output += "!skip [queue number]   Ends playback of the selected audio\n"
        output += "                         if no number is provided, ends playback of the current audio\n"
        output += "!queue                 Displays the audio currently in the queue\n"
        output += "```"
        await ctx.channel.send(output)


    async def leave_channel(self, guild):
        if guild.voice_client is not None and guild.id in self.queue:
            del self.queue[guild.id]
            await guild.voice_client.disconnect()
            print("disconnected from vc")
            await self.client.change_presence(activity=discord.Game('her lyre'))
            return True
        else:
            return False


    async def join_channel(self, voice_client, channel):
        if voice_client is None:
            vc = await channel.connect()
            self.queue[channel.guild.id] = []
            print("connected to vc")
            await self.client.change_presence(activity=discord.Game('ly.radio'))
        elif voice_client.channel != channel:
            await ctx.voice_client.move_to(channel)


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def join(self, ctx):
        """ Joins the user's voice channel """
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            await self.join_channel(ctx.voice_client, channel)
        else:
            await ctx.channel.send("*shrugs*")


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def leave(self, ctx):
        """ Leaves the voice channel """
        if await self.leave_channel(ctx.guild):
            await ctx.channel.send("Later!")
        else:
            await ctx.channel.send("I'm not even in a voice channel though...")


    def play_next(self, ctx, err=None):
        if err:
            print("play_next caught error:")
            print(err)
        if ctx.guild.id in self.queue and len(self.queue[ctx.guild.id]) > 0:
            player = self.queue[ctx.guild.id].pop(0)
            ctx.guild.voice_client.play(player, after=lambda e: self.play_next(ctx, e))
            print("play_next playing next song: " + player.title)


    @commands.command(aliases = ["play"])
    async def vplay(self, ctx, *search):
        """ Plays or queues audio from the url or search term """
        search = " ".join(search)
        server = ctx.guild

        if ctx.author.voice and ctx.author.voice.channel:
            await self.join(ctx)

        voice_client = ctx.voice_client

        if voice_client is None or ctx.guild.id not in self.queue:
            await ctx.channel.send("Maybe if I were already in vchat, but I'm not feeling it...")
            return

        url = search
        await ctx.channel.send("Searching...")
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.client.loop)
            if player:
                await ctx.channel.send("Gotcha, queueing " + player.title + ", " + ctx.author.name)
                self.queue[ctx.guild.id].append(player)
            else:
                await ctx.channel.send("Can't do that " + ctx.message.author.name)

            if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                print("Nothing was in queue when " + player.title + " was queued")
                self.play_next(ctx)


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def pause(self, ctx):
        """ Pauses playback of the current audio """
        if ctx.voice_client and ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
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
    async def skip(self, ctx, index:int = 0):
        """ Skips the current song

        if no number is provided, ends playback of the current audio
        """
        if ctx.guild.id not in self.queue:
            await ctx.channel.send("lol good one")
            return

        if index == 0:
            await ctx.channel.send("Skipping current song")
            ctx.voice_client.stop()
        elif index > 0 and len(self.queue[ctx.guild.id]) >= index:
            await ctx.channel.send("Removing " + str(index) + ": " + self.queue[ctx.guild.id][index-1].title)
            del self.queue[ctx.guild.id][index - 1]
        else:
            await ctx.channel.send("Y'know, I'm not really sure what that number means...")
            

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def queue(self, ctx):
        """ Displays the audio currently in the queue """
        output = ""

        if ctx.guild.id in self.queue:
            for index, queued in enumerate(self.queue[ctx.guild.id]):
                output += str(index + 1) + ": " + queued.title + "\n"
        else:
            await ctx.channel.send("Am I even in vchat?")
            return
        if output != "":
            await ctx.channel.send(output)
        else:
            await ctx.channel.send("No songs in queue")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        vchannel = before.channel
        if vchannel and vchannel.guild.id in self.queue:
            vc = vchannel.guild.voice_client
            if vc and len(vc.channel.members) == 1:
                await self.leave_channel(vchannel.guild)


    #def cog_unload():
    #    for guild in thing:
    #        self.leave_channel(guild)



def setup(client):
    client.add_cog(vchat(client))

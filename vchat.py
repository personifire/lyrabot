import discord
from discord.ext import commands
import discord.errors
import youtube_dl

ytdl_format_options = {
    'format': 'bestaudio/best',
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
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class vchat(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = {}

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def vchat(self, ctx):
        output =""
        output += "*!join* - Joins the user's voice channel\n"
        output += "*!leave* - Leaves the voice channel\n"
        output += "*!vplay* [url] OR [\"search term\"] - Plays or queues audio from the url or searched video in the voice channel after a short delay\n"
        output += "*!pause* - Pauses the audio currently playing in the voice channel\n"
        output += "*!skip [queue number]*  - Ends playback of the selected audio\n"
        output += "      if no number is provided, ends playback of the current audio\n"
        output += "*!resume* - Resumes playback of the current audio\n"
        output += "*!queue* - Displays the audio currently in the queue\n"
        await ctx.channel.send(output)


    async def join_channel(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel

            if ctx.voice_client is None:
                self.queue[ctx.guild.id] = []
                vc = await channel.connect()
                print("connected to vc")
                await self.client.change_presence(activity=discord.Game(name='ly.radio'))
            elif ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to(channel)
        else:
            await ctx.channel.send("*shrugs*")



    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def join(self, ctx):
        await self.join_channel(ctx)



    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            del self.queue[ctx.guild.id]
            await ctx.voice_client.disconnect()
            print("disconnected from vc")
            await self.client.change_presence(activity=discord.Game(name='her lyre'))
        else:
            await ctx.channel.send("I'm not even in a voice channel though...")



    def play_next(self, ctx, err=None):
        if err:
            print(err)
            ctx.channel.send("Something went wrong!")

        if len(self.queue[ctx.guild.id]) > 0:
            player = self.queue[ctx.guild.id].pop(0)
            ctx.voice_client.play(player, after=lambda e: self.play_next(ctx, e))
        else:
            pass # done playing



    @commands.command()
    async def vplay(self, ctx, *search):
        if ctx.voice_client is None:
            await ctx.channel.send("Tell me to join first!")
            return   

        search = " ".join(search)
        server = ctx.guild

        if ctx.author.voice and ctx.author.voice.channel:
            await self.join_channel(ctx)

        voice_client = ctx.voice_client

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
                self.play_next(ctx)



    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            ctx.voice_client.pause()
        else:
            await ctx.channel.send("Can't pause if a song isn't playing!")


    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        else:
            await ctx.channel.send("Can't resume if a song isn't paused!")


    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def skip(self, ctx, index = 0):
        if index == 0:
            await ctx.channel.send("Skipping current song")
            ctx.voice_client.stop()
        elif index > 0 and ctx.voice_client in self.queue and len(self.queue[ctx.guild.id]) > index:
            await ctx.channel.send("Removing " + str(index) + ": " + self.queue[ctx.guild.id][index-1].title)
            del self.queue[ctx.guild.id][index - 1]
            

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def queue(self, ctx):
        output = ""

        if ctx.voice_client in self.queue:
            for index, queued in self.queue[ctx.guild.id]:
                output += str(index + 1) + ": " + queued.title + ", " + str(queued.duration) + "s\n"
        if output != "":
            await ctx.channel.send(output)
        else:
            await ctx.channel.send("No songs in queue")



def setup(client):
    client.add_cog(vchat(client))

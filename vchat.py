import discord
from discord.ext import commands
import discord.errors
import youtube_dl

#https://www.youtube.com/watch?v=12_WnaPmPI0

class vchat:
    def __init__(self, client):
        self.client = client
        
    global players
    players = {}
    global queues
    queues = {}


    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.server)
    async def vchat(self):
        output =""
        output += "*!join* - Joins the user's voice channel\n"
        output += "*!leave* - Leaves the voice channel\n"
        output += "*!play* [url] OR [\"search term\"] - Plays or queues audio from the url or searched video in the voice channel after a short delay\n"
        output += "*!pause* - Pauses the audio currently playing in the voice channel\n"
        output += "*!skip [queue number]*  - Ends playback of the selected audio\n"
        output += "      if no number is provided, ends playback of the current audio\n"
        output += "*!resume* - Resumes playback of the current audio\n"
        output += "*!queue* - Displays the audio currently in the queue\n"
        await self.client.say(output)

    
    def check_queue(id):
        global queues
        players[id] = queues[id].pop(0)
        players[id].volume = 0.25
        players[id].start()


    @commands.command(pass_context=True)
    @commands.cooldown(1, 3, commands.BucketType.server)
    async def join(self, ctx):
        if not self.client.is_voice_connected(ctx.message.server) and ctx.message.author.voice.voice_channel:
            await self.client.join_voice_channel(ctx.message.author.voice.voice_channel)
            await self.client.change_presence(game=discord.Game(name='ly.radio'))
        else:
            await self.client.say("*shrugs*")
                

    @commands.command(pass_context=True)
    @commands.cooldown(1, 15, commands.BucketType.server)
    async def leave(self, ctx):
        server = ctx.message.server
        if self.client.is_voice_connected(server):
            voice_client = self.client.voice_client_in(server)
            await voice_client.disconnect()
            await self.client.change_presence(game=discord.Game(name='her lyre'))
        else:
            await self.client.say("I'm not even in a voice channel though...")



    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.server)
    async def play(self, ctx):
        
        server = ctx.message.server

        if not self.client.is_voice_connected(server) and ctx.message.author.voice.voice_channel:
            await self.client.join_voice_channel(ctx.message.author.voice.voice_channel)
            await self.client.change_presence(game=discord.Game(name='ly.radio'))
        
        voice_client = self.client.voice_client_in(server)

        await self.client.say("Searching...")
        await self.client.send_typing(ctx.message.channel)

        message = []
        message = ctx.message.content.split()
        if len(message) > 1:
            counter = 1
            url = ""
            while(counter < len(message)):
                  url += str(" " + message[counter])
                  counter += 1
        
		if server.id not in players or not players[server.id].is_playing():
            player = await voice_client.create_ytdl_player(url, ytdl_options={'default_search': 'auto'}, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", after=lambda: vchat.check_queue(server.id))
            if player:
                players[server.id] = player
                players[server.id].volume = 0.25
                players[server.id].start()
                await self.client.say("You got it " + ctx.message.author.name + ", playing " + player.title)
            else:
                await self.client.say("Can't do that " + ctx.message.author.name)
            
        else:
            player = await voice_client.create_ytdl_player(url, ytdl_options={'default_search': 'auto'}, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", after=lambda: vchat.check_queue(server.id))
            if player:
                if server.id in queues:
                    queues[server.id].append(player)
                else:
                    queues[server.id] = [player]
                await self.client.say("Gotcha, queueing " + player.title + ", " + ctx.message.author.name)
            else:
                await self.client.say("Can't do that " + ctx.message.author.name)


    @commands.command(pass_context=True)
    @commands.cooldown(1, 3, commands.BucketType.server)
    async def pause(self, ctx):
        id = ctx.message.server.id
        players[id].pause()


    @commands.command(pass_context=True)
    @commands.cooldown(1, 1, commands.BucketType.server)
    async def skip(self, ctx, index = 0):
        if index == 0:
            await self.client.say("Skipping " + players[ctx.message.server.id].title)
            players[ctx.message.server.id].stop()
        elif index > 0 and ctx.message.server.id in queues:
            await self.client.say("Removing " + str(index) + ": " + queues[ctx.message.server.id][index-1].title)
            del queues[ctx.message.server.id][index-1]
            

    @commands.command(pass_context=True)
    @commands.cooldown(1, 3, commands.BucketType.server)
    async def resume(self, ctx):
        id = ctx.message.server.id
        players[id].resume()


    @commands.command(pass_context = True)
    @commands.cooldown(1, 5, commands.BucketType.server)
    async def queue(self, ctx):
        server = ctx.message.server.id
        output = ""
        counter = 1
        if server in players:
            output += "Now Playing: " + players[server].title + "\n"
        if server in queues:
            for queued in queues[server]:
                output += str(counter) + ": " + queued.title + ", " + str(queued.duration) + "s\n"
                counter += 1
        if output != "":
            await self.client.say(output)
        else:
            await self.client.say("No songs in queue")
                

            
def setup(client):
    client.add_cog(vchat(client))

import discord
from discord.ext import commands
import asyncio
import sys

#https://discordpy.readthedocs.io/en/latest/api.html#user
#https://discordapp.com/oauth2/authorize?&client_id=YOUR_CLIENT_ID_HERE&scope=bot&permissions=0
#https://discordapp.com/oauth2/authorize?&client_id=495322560188252170&scope=bot&permissions=53709888

Client = discord.Client(status = "her lyre")
client = commands.Bot(command_prefix = '!')
client.remove_command('help')

STAR = "410660094083334155"
EXTENSIONS = ['react', 'fun', 'search', 'vchat', 'uno']

status = True
prepare = False

loop = asyncio.get_event_loop()

######################################################################################################################

@client.event
async def on_ready():
    print("Lyra is online")

@client.event
async def on_resumed():
    print("Lyra has reconnected")

@client.event
async def on_command_error(err, ctx):
    try:
        if isinstance(err, commands.CommandOnCooldown):
            await ctx.message.channel.send("You're on cooldown, " + ctx.message.author.display_name)
        else:
            await ctx.message.channel.send("Something bad happened! I can't do that, sorry.")
            print(err)
    except Exception as e:
        print("Exception in on_command_error: \n" + str(e))

@client.event
async def on_member_remove(member):
    for channel in member.guild.channels:
        if channel.name == "lyra":
            lyra = channel
    await lyra.send(member.display_name + ' has left the server')

@client.event
async def on_member_join(member):
    await client.add_roles(member, discord.utils.get(member.guild.roles, name = 'everypony'))

@client.event
async def on_message(message):
    if message.content and not message.author.bot:
        if message.content == "Can I boop you?":
            await message.channel.send("*gasp* but that's lewd!")

        elif "screwbot " in message.content.lower() or " screwbot" in message.content.lower() or "screwbot" == message.content.lower():
            await message.channel.send("<a:headcannonL:532554000818634783><:screwbot:532520479290818560><a:headcannonR:532554001321951262>")

        elif 'hands ' in message.content.lower() or ' hands' in message.content.lower() or 'hands' == message.content.lower():
            await message.channel.send("<:mfw:532548719510552586>")

        elif ':' in message.content.lower():
            new = message.content.lower().replace(":", "")
            if "apples" in new:
                await message.channel.send("<:apples:525139683395764244>")
            elif "angery" in new:
                await message.channel.send("<a:angery:525142734684815370>")
            elif "blep" in new:
                await message.channel.send("<:blep:532497085254205450>")
            elif "dab" in new:
                await message.channel.send("<:dab:531755608467046401>")
            elif "default" in new:
                await message.channel.send("<a:default:531762705128751105>")
            elif "excite" in new:
                await message.channel.send("<a:excite:525138734145077259>")
            elif "flyra" in new:
                await message.channel.send("<a:flyra:531755302996148237>")
            elif "lyravator" in new:
                await message.channel.send("<a:lyravator:531772198910689280>")
            elif "scared" in new:
                await message.channel.send("<:scared:532497591426875394>")
            elif "swiggityswooty" in new:
                await message.channel.send("<a:swiggityswooty:531779000251580416>")
            elif "thonk" in new:
                await message.channel.send("<:thonk:532534756093460481>")

        elif 'lyra' in message.content.lower() and 'play' in message.content.lower():
            if 'despacito' in message.content.lower():
                await message.channel.send('https://youtu.be/kJQP7kiw5Fk')
            elif 'sinking' in message.content.lower() and 'ships' in message.content.lower():
                await message.channel.send(' https://youtu.be/Tw09Lrf4EQc')
            elif 'lullaby for a princess' in message.content.lower():
                await message.channel.send('https://youtu.be/H4tyvJJzSDk')
            elif 'hold on' in message.content.lower():
                await message.channel.send('https://youtu.be/ryi-Iy0VyWs')
            elif 'wow glimmer' in message.content.lower():
                await message.channel.send('https://youtu.be/12_WnaPmPI0')
            elif 'discord' in message.content.lower():
                await message.channel.send('https://youtu.be/xPfMb50dsOk')

        if client.user.display_name in message.content.lower():
            if 'hi' in message.content.lower() or 'hello' in message.content.lower() or 'sup' in message.content.lower():
                await message.channel.send('Hi ' + message.author.display_name + '!')
            if 'rolls' in message.content.lower():
                await message.channel.send("<:smuglyra:543975500562038784>")
        if "u lil shid" in message.content.lower():
            await message.channel.send('*pbbbtthhhhhh*')
        if "hmmnah.mp4" in message.content.lower():
            await client.send_file(message.channel, "files/hmmnah.mp4")
        if "lyra" in message.content.lower() and "best" in message.content.lower() and "not" not in message.content.lower():
            await message.channel.send('*blushes*')

        await client.process_commands(message)

######################################################################################################################


@client.command()
@commands.cooldown(1, 45, commands.BucketType.channel)
async def help():
    output = ""
    output += "*!avatar [@user]* - Returns a url of the users avatar\n"
    output += "*!bon* - sends a bon back at you\n"
    output += "*!boop [@user]* - The most heinous of crimes\n"
    output += "*!emote [:emote:] -anim* - Returns a url of the emote'\n"
    output += "    append a *-anim* to retrieve the gif of an animated emote\n"
    output += "*!flip* - Flips a coin\n"
    output += "*!kill [@user]* - kills in style\n"
    output += "*!pop* - :pop:\n"
    output += "*!react* - Lists all emotes Lyra is capable of using\n"
    output += "*!roll [number]* - Rolls a dice, defaults to 20\n"
    output += "*!rr* - Russian Roulette, try not to get shot\n"
    output += "*!search* [tag] - Searches Derpibooru for a random image.\n"
    output += "      Can take either commas or spaces between search terms\n"
    output += "      If using spaces between tags, use '_' for internal spaces\n"
    output += "      EX: 'lyra_heartstrings cute' will search for lyra + cute\n"
    output += "      if no tags are added a random image will be pulled up\n"
    output += "      No anthro or grimdark content!\n"
    output += "*!tableflip* - Flips a table\n"
    output += "*!uno* - Displays the list of commands for Uno\n"
    output += "*!vchat* - Displays the list of commands for the voice channel\n"
    await client.say(output)

@client.command()
@commands.cooldown(2, 7, commands.BucketType.user)
async def bon():
    await client.say('bon')

@client.command(pass_context = True)
@commands.cooldown(2, 7, commands.BucketType.user)
async def avatar(ctx):
    await client.send_typing(ctx.message.channel)
    await client.say(ctx.message.mentions[0].avatar_url.replace('webp', 'png'))

@client.command(pass_context = True)
@commands.cooldown(2, 7, commands.BucketType.user)
async def emote(ctx):
    await client.send_typing(ctx.message.channel)
    emotes = list(client.get_all_emojis())
    i = len(emotes)
    found = False
    name = ctx.message.content.replace("!emote ", "")
    name = name.replace(":", "")
    name = name.replace("<", "")
    name = name.replace(">", "")
    name = name.replace(" -anim", "")
    name = name.replace("-anim", "")
    for looper in range(10):
        name = name.replace(str(looper), "")
        
    while i > 0 and not found:
        i -= 1
        if emotes[i].name == name:
            found = True
    if found:
        if "-anim" in ctx.message.content.lower():
            await client.say(emotes[i].url.replace("png", "gif"))
        else:
            await client.say(emotes[i].url)
    else:
        await client.say("*shrugs*")
        print(name + ":")

@client.command(pass_context = True)
async def dm(ctx):
    await ctx.message.author.send("bon")

@client.command(pass_context = True)
async def nuke(ctx):
    global prepare
    
    if ctx.message.author.id == STAR:
        if(prepare):
            msg = ""
            for i in range(10):
                msg += "<:dab:531755608467046401>\n"
            for i in range(10):
                await client.say(msg)
            prepare = False
        else:
            await client.say("You're gonna have a bad time. Cont?")
            prepare = True
    else:
        await client.say("You're not the boss of me!")

@client.command(pass_context = True)
async def snuggle(ctx):
    if ctx.message.author.id != STAR:
        return
    global status
    if status:
        status = not status
        await client.change_presence(game=discord.Game(name='with her husbando'))
    else:
        status = not status
        await client.change_presence(game=discord.Game(name='her lyre'))

@client.command(pass_context=True)
async def rest(ctx):
    if ctx.message.author.id == STAR:
        await client.say("<:sleepytwi:483862389347844116>")
        id = ctx.message.guild.id
        await client.close()
        print('Lyra is offline')
    elif ctx.message.author.id != STAR:
        await client.say("You're not the boss of me!")

######################################################################################################################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        TOKEN = sys.argv[1]

    all_extensions_loaded = True
    for extension in EXTENSIONS:
        try:
            client.load_extension(extension)
            print('Loaded {}'.format(extension))
        except Exception as error:
            print('{} cannot be loaded. [{}]'.format(extension, error))
            all_extensions_loaded = False
    if all_extensions_loaded:
        client.run(TOKEN)
    else:
        print("Process aborted")
print("Process ended")

try:
    client.logout().send(None)
except StopIteration:
    print("Client stopped")

quit()

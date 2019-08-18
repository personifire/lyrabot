import discord
from discord.ext import commands
import asyncio

#https://discordpy.readthedocs.io/en/latest/api.html#user
#https://discordapp.com/oauth2/authorize?&client_id=YOUR_CLIENT_ID_HERE&scope=bot&permissions=0
#https://discordapp.com/oauth2/authorize?&client_id=495322560188252170&scope=bot&permissions=53709888

Client = discord.Client()
client = commands.Bot(command_prefix = '!')
client.remove_command('help')

STAR = "410660094083334155"
LYRA = "495322560188252170"
CHANNEL = "494919888629006356"
EXTENSIONS = ['react', 'fun', 'search', 'vchat']
IGNORED = (commands.CommandOnCooldown, commands.CommandNotFound)
DC = "495322151252131840"


status = True
prepare = False

loop = asyncio.get_event_loop()


######################################################################################################################


@client.event
async def on_ready():
    print("Lyra is online")
    await client.change_presence(game=discord.Game(name='her lyre'))

@client.event
async def on_resumed():
    print("Lyra has reconnected")

"""
@client.event
async def on_command_error(err, ctx):
    if isinstance(err, IGNORED):
        return
    elif isinstance(err, commands.MissingRequiredArgument):
        await client.send_message(ctx.message.channel, "Gimme something to work with here")
    elif isinstance(err, TypeError):
        await client.send_message(ctx.message.channel, "I don't know how to do that")
    else:
        print("Command: " + ctx.message.content + "\nError: ")
        print(err)
"""

@client.event
async def on_member_remove(member):
    for channel in member.server.channels:
        if channel.name == "lyra":
            lyra = channel
    await client.send_message(lyra, '' + member.display_name + ' has left the server')

@client.event
async def on_member_join(member):
    await client.add_roles(member, discord.utils.get(member.server.roles, name = ''))


@client.event
async def on_message(message):
    if message.content and not message.author.bot:
        
        if message.content == "Can I boop you?":
            await client.send_message(message.channel, "*gasp* but that's lewd!")

        elif "screwbot " in message.content.lower() or " screwbot" in message.content.lower() or " screwbot " in message.content.lower() or "screwbot" == message.content.lower():
            await client.send_message(message.channel, "<a:headcannonL:532554000818634783><:screwbot:532520479290818560><a:headcannonR:532554001321951262>")

        elif 'hands ' in message.content.lower() or ' hands ' in message.content.lower() or ' hands' in message.content.lower() or 'hands' == message.content.lower():
            await client.send_message(message.channel, "<:mfw:532548719510552586>")

        elif ':' in message.content.lower():
            new = message.content.lower().replace(":", "")
            if "apples" in new:
                await client.send_message(message.channel, "<:apples:525139683395764244>")
            elif "angery" in new:
                await client.send_message(message.channel, "<a:angery:525142734684815370>")
            elif "blep" in new:
                await client.send_message(message.channel, "<:blep:532497085254205450>")
            elif "dab" in new:
                await client.send_message(message.channel, "<:dab:531755608467046401>")
            elif "default" in new:
                await client.send_message(message.channel, "<a:default:531762705128751105>")
            elif "excite" in new:
                await client.send_message(message.channel, "<a:excite:525138734145077259>")
            elif "flyra" in new:
                await client.send_message(message.channel, "<a:flyra:531755302996148237>")
            elif "lyravator" in new:
                await client.send_message(message.channel, "<a:lyravator:531772198910689280>")
            elif "scared" in new:
                await client.send_message(message.channel, "<:scared:532497591426875394>")
            elif "swiggityswooty" in new:
                await client.send_message(message.channel, "<a:swiggityswooty:531779000251580416>")
            elif "thonk" in new:
                await client.send_message(message.channel, "<:thonk:532534756093460481>")


        elif 'lyra' in message.content.lower() and 'play' in message.content.lower():
            if 'despacito' in message.content.lower():
                await client.send_message(message.channel, 'https://youtu.be/kJQP7kiw5Fk')
            elif 'sinking' in message.content.lower() and 'ships' in message.content.lower():
                await client.send_message(message.channel, ' https://youtu.be/Tw09Lrf4EQc')
            elif 'lullaby for a princess' in message.content.lower():
                await client.send_message(message.channel, 'https://youtu.be/H4tyvJJzSDk')
            elif 'hold on' in message.content.lower():
                await client.send_message(message.channel, 'https://youtu.be/ryi-Iy0VyWs')
            elif 'wow glimmer' in message.content.lower():
                await client.send_message(message.channel, 'https://youtu.be/12_WnaPmPI0')
            elif 'discord' in message.content.lower():
                await client.send_message(message.channel, 'https://youtu.be/xPfMb50dsOk')

                
        if client.user.display_name in message.content.lower():
            if 'hi' in message.content.lower() or 'hello' in message.content.lower() or 'sup' in message.content.lower():
                await client.send_message(message.channel, 'Hi ' + message.author.display_name + '!')
            if 'rolls' in message.content.lower():
                await client.send_message(message.channel, "<:smuglyra:543975500562038784>")
        if "u lil shid" in message.content.lower():
            await client.send_message(message.channel, '*pbbbtthhhhhh*')
        if "hmmnah.mp4" in message.content.lower():
            await client.send_file(message.channel, "files/hmmnah.mp4")
        if "lyra" in message.content.lower() and "best" in message.content.lower() and "not" not in message.content.lower():
            await client.send_message(message.channel, '*blushes*')

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
    output += "*!search* [tag] - Searches Derpibooru for a random image,\n"
    output += "      supports up to 5 tags, no explicit or grimdark content\n"
    output += "      use '_' for spaces in tags, and spaces between tag,\n"
    output += "      EX: 'lyra_heartstrings cute' will search for lyra + cute\n"
    output += "      if no tags are added a random image will be pulled up\n"
    output += "*!tableflip* - Flips a table\n"
    ##output += "*!uno* - Displays the list of commands for Uno\n"
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
    await client.send_message(ctx.message.author, "bon")

@client.command(pass_context = True)
async def nuke(ctx):
    global prepare
    
    if ctx.message.author.id == STAR:
            if(prepare):
                i = 0
                while(i < 15):
                    await client.say("<:dab:531755608467046401>")
                    i+= 1
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
        id = ctx.message.server.id
        await client.close()
        print('Lyra is offline')
    elif ctx.message.author.id != STAR:
        await client.say("You're not the boss of me!")


######################################################################################################################

def run_client(client, *args, **kwargs):
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(client.start(*args, **kwargs))
        except Exception as e:
            print("Error", e)  # or use proper logging
        print("Waiting until restart")
        time.sleep(600)

if __name__ == "__main__":

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
input("Wait")

quit()

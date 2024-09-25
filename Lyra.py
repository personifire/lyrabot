import asyncio
import logging
import sys
import os

import asyncpg
import discord
from discord.ext import commands

# logger will eat exception and error messages
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

STAR = 410660094083334155
PERS = 347100862125965312

EXTDIR = "cogs"

owners = [PERS]
owners = set(owners)

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

allowed_mentions = discord.AllowedMentions(replied_user = False)

bot = commands.Bot(
        command_prefix = '!',
        case_insensitive = True,
        intents = intents,
        allowed_mentions = allowed_mentions,
        owner_ids = owners
)

status = True

############################################## EVENTS ##############################################

@bot.event
async def on_ready():
    print("Lyra is online")

@bot.event
async def on_resumed():
    print("Lyra has reconnected")

@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.CommandOnCooldown):
        await ctx.send(f"You're on cooldown for another {round(err.retry_after)}s, {ctx.author.display_name}")
    elif isinstance(err, commands.NoPrivateMessage):
        await ctx.send("Sorry, that command doesn't work in PMs!")
    elif isinstance(err, commands.UserNotFound) or isinstance(err, commands.MemberNotFound):
        await ctx.send("Who?")
    else:
        raise err # gotta log them somewhere

@bot.event
async def on_member_remove(member):
    lyra = None
    for channel in member.guild.channels:
        if channel.name == "lyra":
            lyra = channel
    if lyra is not None:
        await lyra.send(member.display_name + ' has left the server')
    else:
        print(member.display_name + " left server: " + member.guild.name)

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name = 'everypony')
    if role:
        await member.add_roles(role)

############################################## COMMANDS ##############################################


@bot.command()
@commands.cooldown(2, 7, commands.BucketType.user)
async def bon(ctx):
    """ bon """
    await ctx.channel.send('bon')

@bot.command()
async def dm(ctx):
    """ also bon """
    await ctx.message.author.send("bon")

@bot.command()
async def nuke(ctx, *args):
    """ :dab: """
    author = ctx.author
    if author.guild_permissions.administrator:
        msg = ""
        for i in range(10):
            msg += "<:dab:531755608467046401>\n"
        for i in range(5):
            await ctx.channel.send(msg)
    else:
        await ctx.channel.send("You're gonna have a bad time. Might need more perms for that!")

@bot.command()
async def snuggle(ctx):
    """ for snugs """
    if ctx.message.author.id != STAR:
        return
    global status
    if status:
        status = not status
        await bot.change_presence(activity=discord.Game('with some faggo'))
    else:
        status = not status
        await bot.change_presence(activity=discord.Game('her lyre'))

@bot.command()
async def rest(ctx, *args):
    """ For when lyra gets tired """
    if ctx.author.id in owners:
            sleepytwi = discord.utils.get(bot.emojis, name = 'sleepytwi')
            if sleepytwi:
                await ctx.channel.send(sleepytwi)
            else:
                await ctx.channel.send("Alright. Nighty-night!")
            await bot.close()
            print('Lyra is offline')
    else:
        await ctx.channel.send("Aww, but I'm not tired yet!")
        

############################################## RUNNING ##############################################

def get_token():
    tokenloc = "token.txt"
    if len(sys.argv) > 1:
        token = sys.argv[1]
        if not os.path.isfile(tokenloc):
            with open(tokenloc, "w") as tokenfile:
                tokenfile.write(token)
    else:
        if os.path.isfile(tokenloc):
            with open(tokenloc, "r") as tokenfile:
                token = tokenfile.readline().strip()
        else:
            raise Exception("Could not find token")
    return token

async def load_cogs():
    extensions = [os.path.splitext(cog) for cog in os.listdir(EXTDIR) if os.path.isfile(f"{EXTDIR}/{cog}")]
    extensions = [f"{EXTDIR}.{cog}" for cog, ext in extensions if ext == ".py"]
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f'Loaded {extension}')
        except Exception as e:
            print(f'{extension} could not be loaded. [{e}]')
            raise e

async def connect_db():
    bot.db_conn = await asyncpg.connect(host='/var/run/postgresql')

async def main():
    token = get_token()
    await connect_db()
    await load_cogs()

    async with bot:
        await bot.start(token)

    print("Closing bot...")
    await asyncio.gather(bot.close(), bot.db_conn.close())
    print("All done!")
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())

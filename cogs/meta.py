"""
The MIT License (MIT)

Copyright (c) 2015 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import discord
from discord.ext import commands

import asyncio
from contextlib import redirect_stdout
import io
import os
import subprocess
import textwrap
import traceback

EXTDIR = 'cogs'

class meta(commands.Cog):
    def __init__(self, client):
        self.client = client

    def cleanup_code(self, content):
        """ Automatically removes code blocks from the code. """
        # remove leading or trailing '`', '```', ' ', and '\n'
        return content.strip('` \n')


    async def evaluate_code(self, ctx, code):
        """ evaluates a given string of python code in local context

        This code contains many samples taken from https://github.com/Rapptz/RoboDanny
        """
        env = { 'client': self.client, }
        env.update(globals())
        env.update(locals())

        code = self.cleanup_code(code)
        output_capture = io.StringIO()

        funcstr = f'async def func():\n{textwrap.indent(code, "  ")}'
        print("evaluating code:\n" + funcstr + "#----------")

        try:
            exec(funcstr, env)
        except Exception as e:
            return await ctx.send(f'Function definition caught exception:\n```{e.__class__.__name__}: {e}\n```')
        
        func = env['func']
        try:
            with redirect_stdout(output_capture):
                ret = await func()
        except Exception as e:
            value = output_capture.getvalue()
            await ctx.send(f'output:```{value} ```Function run caught exception:```{traceback.format_exc()} ```')
        else:
            value = output_capture.getvalue()
            await ctx.message.add_reaction('\u2705')

            if ret is None:
                if value:
                    await ctx.send(f'output:```{value}```')
            else:
                self._last_result = ret
                await ctx.send(f'output:```{value} ```returned:```{ret} ```')


    @commands.command()
    @commands.is_owner()
    async def wait(self, ctx, delay: int, *, code = ""):
        """ evaluates a given block of python code in the local context after a given delay in seconds """
        if not delay:
            await ctx.send("I need a time delay in seconds, please!")
            return
        if not code:
            await ctx.send("Give me some code to run! I have all globals, locals, and `client` in scope. Indent with two spaces, please.")
            return
        await ctx.channel.send("Gotcha!")

        self.client.loop.call_later(delay, asyncio.ensure_future, self.evaluate_code(ctx, code))


    @commands.command(aliases = ["exec"])
    @commands.is_owner()
    async def eval(self, ctx, *, code = ""):
        """ evaluates a given block of python code using the local context """
        if not code:
            await ctx.send("Give me some code to run! I have all globals, locals, and `client` in scope. Indent with two spaces, please.")
            return
        await ctx.channel.send("Gotcha!")

        await self.evaluate_code(ctx, code)


    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension = None):
        """ Loads the named extension. """
        if extension is None:
            ctx.send("You didn't name a cog to load, you doof")
        
        extension = f"{EXTDIR}.{extension}"

        # duplicate code from reload, because I can't be bothered to think about it
        err = pull_from_git()
        if err:
            await ctx.send("Something weird happened on the update. Error was: ```{err}```\n -- Gonna keep going!")

        try:
            try_load(self.client, extension)
            await ctx.send(f"{extension} loaded!")
        except Exception as e:
            print(f'{extension} could not be loaded. [{traceback.format_exc()}]')
            await ctx.send("Load broke!")


    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension = None):
        """ Reloads the named extension. Defaults to reloading all """
        extensions = [os.path.splitext(cog) for cog in os.listdir(EXTDIR) if os.path.isfile(f"{EXTDIR}/{cog}")]
        extensions = [cog for cog, ext in extensions if ext == ".py"]
        to_reload = extensions
        if extension:
            if extension in extensions:
                to_reload = [extension]
            else:
                await ctx.channel.send("I don't think I have that one...")
                return

        to_reload = [f"{EXTDIR}.{cog}" for cog in to_reload]
        await ctx.channel.send("Alright, reloading!")

        err = pull_from_git()
        if err:
            await ctx.send("Something weird happened on the update. Error was: ```{err}```\n -- Gonna keep going!")

        reload_confirm = ""
        reload_deny    = "\n\n"
        for extension in to_reload:
            try:
                try_load(self.client, extension)
                reload_confirm += f"{extension} reloaded!\n"
            except Exception as e:
                reload_deny    += f"{extension} could not be loaded!\n"
                print(f'{extension} could not be loaded. [{traceback.format_exc()}]')
        await ctx.send(reload_confirm + reload_deny)
        await ctx.send("All done!")


def try_load(client, extension):
    try:
        client.load_extension(extension)
        print(f'Loaded {extension}')
    except commands.ExtensionAlreadyLoaded:
        client.reload_extension(extension)
        print(f'Reloaded {extension}')


def pull_from_git():
    try:
        output = subprocess.check_output(["git", "pull"])
        print(output)
        return False
    except Exception as e:
        return f"{traceback.format_exc(limit=1)}"


def setup(client):
    client.add_cog(meta(client))

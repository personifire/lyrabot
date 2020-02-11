import discord
from discord.ext import commands

import asyncio
from contextlib import redirect_stdout
import io
import textwrap
import traceback

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
"""

"""
This code contains many samples taken from https://github.com/Rapptz/RoboDanny
"""

class meta(commands.Cog):
    def __init__(self, client):
        self.client = client

    def cleanup_code(self, content):
        """ Automatically removes code blocks from the code. """
        # remove leading or trailing '`', '```', ' ', and '\n'
        return content.strip('` \n')


    async def evaluate_code(self, ctx, code):
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
        """ evaluates given code 
            heavily "inspired" by https://github.com/Rapptz/RoboDanny """
        if not code:
            await ctx.send("Give me some code to run! I have all globals, locals, and `client` in scope. Indent with two spaces, please.")
            return
        await ctx.channel.send("Gotcha!")

        await self.evaluate_code(ctx, code)



def setup(client):
    client.add_cog(meta(client))

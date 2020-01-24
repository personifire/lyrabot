import discord
from discord.ext import commands

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

    def adjust_indentation(self, content):
        """ Tries to automatically adjust indentation to be two spaces """
        # TODO not sure if entirely feasible
        return content

    def cleanup_code(self, content):
        """ Automatically removes code blocks from the code. """
        # remove leading or trailing '`', '```', ' ', and '\n'
        content = content.strip('` \n')

        # adjust indentation to be two spaces
        return self.adjust_indentation(content)


    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        """ evaluates given code 
            heavily "inspired" by https://github.com/Rapptz/RoboDanny """
        if not code:
            await ctx.send("Give me some code to run! I have all globals, locals, and `client` in scope. Indent with two spaces, please.")
            return
        env = { 'client': self.client, }
        env.update(globals())
        env.update(locals())

        code = self.cleanup_code(code)
        output_capture = io.StringIO()

        funcstr = f'async def func():\n{textwrap.indent(code, "  ")}'

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
            await ctx.channel.send("Gotcha!")

            if ret is None:
                if value:
                    await ctx.send(f'output:```{value}```')
            else:
                self._last_result = ret
                await ctx.send(f'output:```{value} ```returned:```{ret} ```')



def setup(client):
    client.add_cog(meta(client))

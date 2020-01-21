import discord
from discord.ext import commands

from contextlib import redirect_stdout
import io
import textwrap
import traceback

class meta(commands.Cog):
    def __init__(self, client):
        self.client = client

    def cleanup_code(self, content):
        """ Automatically removes code blocks from the code. """
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        """ evaluates given code 
            heavily "inspired" by https://github.com/Rapptz/RoboDanny """
        env = {
                'client': self.client,
              }
        env.update(globals())
        env.update(locals())

        code = self.cleanup_code(code)
        output_capture = io.StringIO()

        funcstr = f'async def func():\n{textwrap.indent(code, "  ")}'

        try:
            exec(funcstr, env)
        except Exception as e:
            return await ctx.send(f'Caught an exception:\n```{e.__class__.__name__}: {e}\n```')
        
        func = env['func']
        try:
            with redirect_stdout(output_capture):
                ret = await func()
        except Exception as e:
            value = output_capture.getvalue()
            await ctx.send(f'```{value}```Caught an exception:```{traceback.format_exc()}```')
        else:
            value = output_capture.getvalue()
            try:
                await ctx.message.add_reaction('\u1ffd')
                await ctx.channel.send("Gotcha!")
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```{value}```')
            else:
                self._last_result = ret
                await ctx.send(f'```{value}```Returned:```{ret}```')



def setup(client):
    client.add_cog(meta(client))

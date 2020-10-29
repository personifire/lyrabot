import discord
from discord.ext import commands

import asyncio
import random
import re

class admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_guild_permissions(manage_roles = True)
    @commands.bot_has_guild_permissions(manage_roles = True)
    async def selfassign(self, ctx, *, role: discord.Role):
        msg = "Use any reaction to this post to self-assign the " 
        msg += "**" + role.name + "** (id: " + str(role.id) + ")"
        msg += " role! Or remove (or react then remove) to self-remove the role."

        await ctx.send(msg)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, rawreactevent):
        await self.react_change_role(rawreactevent)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, rawreactevent):
        await self.react_change_role(rawreactevent)

    async def react_change_role(self, rawreactevent):
        try:
            guild   = discord.utils.get(self.client.guilds, id=rawreactevent.guild_id)
            channel = guild.get_channel(rawreactevent.channel_id)
            message = await channel.fetch_message(rawreactevent.message_id)

            if guild is None:
                return

            if message.author == guild.me:
                msgregexstr  = "^Use any reaction to this post to self-assign the .*(\(id: (.*)\)) role!"
                msgregexstr += " Or remove \(or react then remove\) to self-remove the role.$"
                msgregex = re.compile(msgregexstr)
                match = msgregex.match(message.content)
                if match:
                    roleid = int(match.group(2))
                    user = guild.get_member(rawreactevent.user_id)
                    role = guild.get_role(roleid)
                    if rawreactevent.event_type == "REACTION_ADD":
                        await user.add_roles(role)
                    elif rawreactevent.event_type == "REACTION_REMOVE":
                        await user.remove_roles(role)
        except Exception as e:
            raise e

    @commands.command()
    @commands.has_guild_permissions(manage_roles = True)
    @commands.bot_has_guild_permissions(manage_roles = True)
    async def holiday(self, ctx, num_roles: int):
        """ Creates a number of new roles, and assigns exactly one of each to each member. """
        roles = [await ctx.guild.create_role(name = "holiday " + str(rolenum + 1)) for rolenum in range(num_roles)]
        role_selection = []
        for index, member in enumerate(ctx.guild.members):
            if len(role_selection) == 0:
                role_selection = [role for role in roles] * 2
                shuffle(role_selection)
            await member.add_roles(role_selection.pop())
            asyncio.sleep(1)



def setup(client):
    client.add_cog(admin(client))

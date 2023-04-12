import discord
from discord.ext import commands

import asyncio
import random
import re

class admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.invite_trackers = {} # should put this in a db but I'm not figuring out how to use one properly for this right now

    @commands.command()
    @commands.has_guild_permissions(manage_roles = True)
    @commands.bot_has_guild_permissions(manage_roles = True)
    async def selfassign(self, ctx, *, role: discord.Role):
        msg = "Use any reaction to this post to self-assign the " 
        msg += "**" + role.name + "** (id: " + str(role.id) + ")"
        msg += " role! Or remove (or react then remove) to self-remove the role."

        await ctx.send(msg)

    @commands.command()
    @commands.has_guild_permissions(manage_guild = True)
    @commands.bot_has_guild_permissions(manage_guild = True) # unfortunate but necessary
    async def toggle_track_invites(self, ctx):
        if ctx.guild.id in self.invite_trackers:
            del self.invite_trackers[ctx.guild.id]
            return await ctx.send("Removed invite tracking.")
        else:
            self.invite_trackers[ctx.guild.id] = {}
            tracker = self.invite_trackers[ctx.guild.id]

            tracker['channel_id'] = ctx.channel.id
            invites = await ctx.guild.invites()
            for invite in invites:
                tracker[invite.id] = invite.uses
            return await ctx.send("Invite tracking enabled! Messages will be sent in this channel.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id in self.invite_trackers:
            tracker = self.invite_trackers[member.guild.id]
            invites = await member.guild.invites()
            for invite in invites:
                if invite.id not in tracker:
                    tracker[invite.id] = 0

                if tracker[invite.id] != invite.uses:
                    print("  invite tracker saw likely used invite")
                    channel = self.client.get_channel(tracker['channel_id'])
                    if not channel: # well, it's better than going into some weird state
                        print(f"invite tracking channel was deleted for guild {member.guild.id} :(")
                        del self.invite_trackers[member.guild.id]
                        return
                    # if we have false positives, we might get multiple hits for a single member -- hopefully not
                    message = f"{member} (snowflake {member.id}) likely joined via invite {invite.url}"
                    if invite.inviter:
                        message += f", made by {invite.inviter}."
                    else:
                        message += '.'
                    await channel.send(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, rawreactevent):
        await self.react_change_role(rawreactevent)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, rawreactevent):
        await self.react_change_role(rawreactevent)

    async def react_change_role(self, rawreactevent):
        try:
            guild   = discord.utils.get(self.client.guilds, id=rawreactevent.guild_id)
            if guild is None:
                return
            channel = guild.get_channel(rawreactevent.channel_id)
            message = await channel.fetch_message(rawreactevent.message_id)

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
    async def persist_roles(self, ctx, *roles):
        """ Backs up current role assignments and permission overrides. 
        
        Will attempt to reassign these roles if a member leaves and rejoins.
        """
        pass

    @commands.command()
    @commands.has_guild_permissions(manage_roles = True)
    @commands.bot_has_guild_permissions(manage_roles = True)
    async def holiday(self, ctx, num_roles: int):
        """ Creates a number of new roles, and assigns exactly one of each to each member. """
        roles = [await ctx.guild.create_role(name = "holiday " + str(rolenum + 1)) for rolenum in range(num_roles)]
        role_selection = []
        for member in ctx.guild.members:
            if len(role_selection) == 0:
                role_selection = [role for role in roles] * 2
                random.shuffle(role_selection)
            await member.add_roles(role_selection.pop())
            await asyncio.sleep(1)



async def setup(client):
    await client.add_cog(admin(client))

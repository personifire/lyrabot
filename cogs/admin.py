import discord
from discord.ext import commands

import asyncio
import random
import re

async def init_tables(db_conn):
    # invite tracker
    await db_conn.execute("""
        CREATE TABLE IF NOT EXISTS inv_tracker_guilds (
            guild_id    bigint PRIMARY KEY,
            channel_id  bigint NOT NULL
        );
    """) 
    await db_conn.execute("""
        CREATE TABLE IF NOT EXISTS inv_trackers (
            inv_id      varchar(20) PRIMARY KEY,
            guild_id    bigint REFERENCES inv_tracker_guilds (guild_id),
            count       integer
        );
    """) 



class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        db_conn = self.bot.db_conn

        record = await db_conn.fetchrow("SELECT * FROM inv_tracker_guilds WHERE guild_id=$1;", ctx.guild.id)
        if record is not None:
            print(f"deleting tracker in guild {ctx.guild.id}")
            # disable tracker
            await db_conn.execute("DELETE FROM inv_tracker_guilds WHERE guild_id=$1;", ctx.guild.id)
            return await ctx.send("Removed invite tracking.")
        else:
            print(f"creating tracker in guild {ctx.guild.id}")
            # enable tracker and initialize invite counts
            query = "INSERT INTO inv_tracker_guilds (guild_id, channel_id) VALUES ($1, $2);"
            await db_conn.execute(query, ctx.guild.id, ctx.channel.id)

            invites = await ctx.guild.invites()
            for invite in invites:
                print(f"  adding tracked invite with id {invite.id}")
                query = "INSERT INTO inv_trackers (inv_id, guild_id, count) VALUES ($1, $2, $3);"
                await db_conn.execute(query, invite.id, ctx.guild.id, invite.uses)
            return await ctx.send("Invite tracking enabled! Messages will be sent in this channel.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.invite_tracker_join(member)

    async def invite_tracker_join(self, member):
        db_conn = self.bot.db_conn

        result = await db_conn.fetchrow("SELECT * FROM inv_tracker_guilds WHERE guild_id=$1;", member.guild.id)
        if result is None:
            return

        channel = self.bot.get_channel(result['channel_id'])
        if channel is None:
            print(f"invite tracking channel was deleted for guild {member.guild.id} :(")
            return await db_conn.execute("DELETE FROM inv_tracker_guilds WHERE guild_id=$1;", member.guild.id)

        tracked_invs = await db_conn.fetch("SELECT * FROM inv_trackers WHERE guild_id=$1;", member.guild.id)
        tracker = {inv['inv_id']: inv['count'] for inv in tracked_invs}

        possible_invites = []
        invites = await member.guild.invites()
        for invite in invites:
            if invite.id not in tracker:
                if invite.uses != 0:
                    possible_invites.append(invite)

                tracker[invite.id] = invite.uses
                query = "INSERT INTO inv_trackers (inv_id, guild_id, count) VALUES ($1, $2, $3);"
                await db_conn.execute(query, invite.id, member.guild.id, invite.uses)

            elif tracker[invite.id] != invite.uses:
                possible_invites.append(invite)
                query = "UPDATE inv_trackers SET count=$1 WHERE inv_id=$2"
                await db_conn.execute(query, invite.uses, invite.id)

        def inv_to_str(inv):
            msg = f"<{inv.url}>"
            if invite.inviter:
                msg += f", made by {inv.inviter.mention} (snowflake {member.id})"
            return msg

        message = f"{member.mention} (snowflake {member.id}) likely joined via"
        if len(possible_invites) == 1:
            message += f" invite {inv_to_str(possible_invites[0])}"
        else:
            message += f" one of the following invites:"
            for inv in possible_invites:
                message += f"\n* {inv_to_str(inv)}"
        await channel.send(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, rawreactevent):
        await self.react_change_role(rawreactevent)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, rawreactevent):
        await self.react_change_role(rawreactevent)

    async def react_change_role(self, rawreactevent):
        try:
            guild   = discord.utils.get(self.bot.guilds, id=rawreactevent.guild_id)
            if guild is None:
                return
            channel = guild.get_channel(rawreactevent.channel_id)
            if channel is None:
                return
            message = await channel.fetch_message(rawreactevent.message_id)
            if message is None:
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
        roles = [await ctx.guild.create_role(name = "holiday {rolenum + 1}") for rolenum in range(num_roles)]
        role_selection = []
        for member in ctx.guild.members:
            if len(role_selection) == 0:
                role_selection = [role for role in roles] * 2
                random.shuffle(role_selection)
            await member.add_roles(role_selection.pop())
            await asyncio.sleep(1)



async def setup(bot):
    await init_tables(bot.db_conn)
    await bot.add_cog(admin(bot))

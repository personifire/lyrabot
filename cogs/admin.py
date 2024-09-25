import discord
from discord.ext import commands

import asyncio
import functools
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

    # TODO completely fucking rewrite role persistence because you FORGOT TO FUCKING PUSH TO GITHUB BEFORE DELETING YOUR OLD AWS SERVER AAAAAAAAAAAAAAAAAAA
    #    - or, just redesign it from the ground up since it's really ugly as is...


class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ################################################################################
    #################################   commands   #################################
    ################################################################################

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

    @commands.command()
    @commands.has_guild_permissions(manage_guild = True)
    @commands.bot_has_guild_permissions(manage_guild = True) # unfortunate but necessary
    async def toggle_track_invites(self, ctx):
        db_conn = self.bot.db_conn

        tracker_enabled = await self._add_guild_record("inv_tracker_guilds", ctx.guild.id, ctx.channel.id)
        if tracker_enabled:
            # initialize invite counts
            invites = await ctx.guild.invites()
            for invite in invites:
                print(f"  adding tracked invite with id {invite.id}")
                query = "INSERT INTO inv_trackers (inv_id, guild_id, count) VALUES ($1, $2, $3);"
                await db_conn.execute(query, invite.id, ctx.guild.id, invite.uses)
            return await ctx.send("Invite tracking enabled! Messages will be sent in this channel.")
        else:
            # get rid of old invite data
            print(f"deleting tracked invites in guild {ctx.guild.id}")
            await db_conn.execute("DELETE FROM inv_trackers WHERE guild_id=$1;", ctx.guild.id)

            # disable tracker
            print(f"deleting invite tracker in guild {ctx.guild.id}")
            await db_conn.execute(f"DELETE FROM inv_tracker_guilds WHERE guild_id=$1;", ctx.guild.id)
            return await ctx.send("Removed invite tracking.")

    @commands.command()
    @commands.has_guild_permissions(manage_roles = True)
    @commands.bot_has_guild_permissions(manage_roles = True)
    async def archive(self, ctx, channel: discord.TextChannel=None):
        """ convert all role overwrites into member overwrites for a given channel """
        if channel is None:
            channel = ctx.channel
        overwrites = channel.overwrites

        for target, overwrite in overwrites.items():
            if not isinstance(target, discord.Role) and not target.is_default():
                continue

            for member in target.members:
                if member != ctx.me:
                    await channel.set_permissions(member, overwrite=overwrite)
            await channel.set_permissions(target, overwrite=None)

    #################################################################################
    #################################   listeners   #################################
    #################################################################################

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.invite_tracker_join(member)

    ################################################################################
    ##############################   event handlers   ##############################
    ################################################################################

    ##### invite tracker #####

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

    #################################################################################
    ##################################   helpers   ##################################
    #################################################################################

    async def _add_guild_record(self, table_name, guild_id, channel_id=None):
        """Create or delete a table entry for a guild
        Returns true if a new entry was created, or false if one already existed.
        """
        db_conn = self.bot.db_conn

        assert(all(char.isalpha() or char == "_" for char in table_name))

        record = await db_conn.fetchrow(f"SELECT * FROM {table_name} WHERE guild_id=$1;", guild_id)
        if record is None:
            print(f"creating entry in {table_name} in guild {guild_id}")
            # enable tracker and initialize invite counts
            if channel_id is not None:
                query = f"INSERT INTO {table_name} (guild_id, channel_id) VALUES ($1, $2);"
                await db_conn.execute(query, guild_id, channel_id)
            else:
                query = f"INSERT INTO {table_name} (guild_id) VALUES ($1);"
                await db_conn.execute(query, guild_id)
            return True
        return False



async def setup(bot):
    await init_tables(bot.db_conn)
    await bot.add_cog(admin(bot))

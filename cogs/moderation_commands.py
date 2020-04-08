import string
import random
from datetime import datetime as dt
import typing

import discord
from discord.ext import commands

from cogs import utils


class ModerationCommands(utils.Cog):

    @staticmethod
    async def get_unused_infraction_id(db, n:int=5) -> str:
        """This method creates a randomisied string to use as the infraction identifier.

        Input Argument: n - Must be int
        Returns: A string n long
        """

        def create_code(n):
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

        while True:
            code = create_code(n)
            is_valid = await db("SELECT infraction_id FROM infractions WHERE infraction_id=$1", code)
            if not is_valid:
                return code

    @utils.Cog.listener()
    async def on_moderator_action(self, moderator:discord.Member, user:discord.User, reason:str, action:str):
        """Looks for moderator actions being done and logs them into the relevant channel"""

        # Save to database
        db_reason = None if reason == '<No reason provided>' else reason
        async with self.bot.database() as db:
            code = await self.get_unused_infraction_id(db)
            await db(
                """INSERT INTO infractions (infraction_id, guild_id, user_id, moderator_id, infraction_type,
                infraction_reason, timestamp) VALUES ($1, $2, $3, $4, $5)""",
                code, moderator.guild.id, user.id, moderator.id, action, db_reason, dt.utcnow(),
            )

        # Get log channel
        log_channel_id = self.bot.guild_settings[moderator.guild_id].get("modmail_channel_id", None)
        log_channel = self.bot.get_channel(log_channel_id)
        if log_channel is None:
            return

        # Make info embed
        with utils.Embed() as embed:
            embed.title = action
            embed.add_field("Moderator", f"{moderator.mention} (`{moderator.id}`)")
            embed.add_field("User", f"<@{user.id}> (`{user.id}`)")
            if reason:
                embed.add_field("Reason", reason, inline=False)

        # Send to channel
        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @utils.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Removed Moderator role from database when its deleted"""

        if role.id == self.bot.guild_settings[role.guild].get("guild_moderator_role_id"):
            self.bot.guild_settings[role.guild]["guild_moderator_role_id"] = None
            async with self.bot.database() as db:
                await db("UPDATE guild_settings SET guild_moderator_role_id = null WHERE guild_id=$1", role.guild.id)

    @commands.command(cls=utils.Command)
    @utils.checks.is_guild_moderator()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def mute(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Mutes a user from the server"""

        # Check if role exists
        muted_role_id = self.bot.guild_settings[ctx.guild.id].get("muted_role_id", None)
        if muted_role_id is None:
            return await ctx.send("There is no mute role set for this server.")

        # Check the user can run the command on who they want
        if user.top_role.position >= ctx.author.top_role.position:
            return await ctx.send("That user is too highly ranked for you to be able to punish them.")
        if user.top_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send("That user is too highly ranked for me to be able to punish them.")

        # Grab the mute role
        mute_role = ctx.guild.get_role(muted_role_id)
        if mute_role is None:
            return await ctx.send("The mute role for this server is set to a deleted role.")
        if mute_role in user.roles:
            return await ctx.send(f"{user.mention} is already muted.")
        if mute_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send("The mute role is too high for me to manage.")

        # DM the user
        dm_reason = f"You have been muted in **{ctx.guild.name}** with the reason `{reason}`."
        try:
            await user.send(dm_reason)
        except discord.Forbidden:
            pass  # Can't DM the user? Oh well

        # Mute the user
        manage_reason = f"{ctx.author!s}: {reason}"
        try:
            await user.add_roles(mute_role, reason=manage_reason)
        except discord.Forbidden:
            return await ctx.send(f"I was unable to add the mute role to {user.mention}.")
        except discord.NotFound:
            return await ctx.send("To me it looks like that user doesn't exist :/")

        # Throw the reason into the database
        self.bot.dispatch("moderation_action", moderator=ctx.author, user=user, reason=reason, action="Mute")

        # Output to chat
        return await ctx.send(f"{user.mention} has been muted by {ctx.author.mention} with reason `{reason}`.")

    @commands.command(cls=utils.Command)
    @utils.checks.is_guild_moderator()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def tempmute(self, ctx:utils.Context, user:discord.Member, duration:utils.TimeValue, *, reason:str='<No reason provided>'):
        """Mutes a user from the server"""

        # Check if role exists
        muted_role_id = self.bot.guild_settings[ctx.guild.id].get("muted_role_id", None)
        if muted_role_id is None:
            return await ctx.send("There is no mute role set for this server.")

        # Check the user can run the command on who they want
        if user.top_role.position >= ctx.author.top_role.position:
            return await ctx.send("That user is too highly ranked for you to be able to punish them.")
        if user.top_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send("That user is too highly ranked for me to be able to punish them.")

        # Grab the mute role
        mute_role = ctx.guild.get_role(muted_role_id)
        if mute_role is None:
            return await ctx.send("The mute role for this server is set to a deleted role.")
        if mute_role in user.roles:
            return await ctx.send(f"{user.mention} is already muted.")
        if mute_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send("The mute role is too high for me to manage.")

        # DM the user
        dm_reason = f"You have been temporarily muted in **{ctx.guild.name}** with the reason `{reason}`."
        try:
            await user.send(dm_reason)
        except discord.Forbidden:
            pass  # Can't DM the user? Oh well

        # Mute the user
        manage_reason = f"{ctx.author!s}: {reason}"
        try:
            await user.add_roles(mute_role, reason=manage_reason)
        except discord.Forbidden:
            return await ctx.send(f"I was unable to add the mute role to {user.mention}.")
        except discord.NotFound:
            return await ctx.send("To me it looks like that user doesn't exist :/")

        # Store the temporary role
        async with self.bot.database() as db:
            await db(
                """INSERT INTO temporary_roles (guild_id, role_id, user_id, remove_timestamp)
                VALUES ($1, $2, $3, $4)""",
                ctx.guild.id, muted_role_id, user.id, dt.utcnow() + duration.delta
            )

        # Throw the reason into the database
        self.bot.dispatch("moderation_action", moderator=ctx.author, user=user, reason=reason, action="Tempmute")

        # Output to chat
        return await ctx.send(f"{user.mention} has been muted for `{duration.clean_spaced}` by {ctx.author.mention} with reason `{reason}`.")

    @commands.command(cls=utils.Command)
    @utils.checks.is_guild_moderator()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def unmute(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Unmutes a user"""

        # Check if role exists
        muted_role_id = self.bot.guild_settings[ctx.guild.id].get("muted_role_id", None)
        if muted_role_id is None:
            return await ctx.send("There is no mute role set for this server.")

        # Check the user can run the command on who they want
        if user.top_role.position >= ctx.author.top_role.position:
            return await ctx.send("That user is too highly ranked for you to be able to punish them.")
        if user.top_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send("That user is too highly ranked for me to be able to punish them.")

        # Grab the mute role
        mute_role = ctx.guild.get_role(muted_role_id)
        if mute_role is None:
            return await ctx.send("The mute role for this server is set to a deleted role.")
        if mute_role not in user.roles:
            return await ctx.send(f"{user.mention} is not muted.")
        if mute_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send("The mute role is too high for me to manage.")

        # DM the user
        dm_reason = f"You have been unmuted in **{ctx.guild.name}** with the reason `{reason}`."
        try:
            await user.send(dm_reason)
        except discord.Forbidden:
            pass  # Can't DM the user? Oh well

        # Mute the user
        manage_reason = f"{ctx.author!s}: {reason}"
        try:
            await user.remove_roles(mute_role, reason=manage_reason)
        except discord.Forbidden:
            return await ctx.send(f"I was unable to remove the mute role from {user.mention}.")
        except discord.NotFound:
            return await ctx.send("To me it looks like that user doesn't exist :/")

        # Throw the reason into the database
        self.bot.dispatch("moderation_action", moderator=ctx.author, user=user, reason=reason, action="Unmute")

        # Remove role from db
        async with self.bot.database() as db:
            await db("DELETE FROM temporary_roles WHERE guild_id=$1 AND role_id=$2 AND user_id=$3", ctx.guild.id, muted_role_id, user.id)

        # Output to chat
        return await ctx.send(f"{user.mention} has been unmuted by {ctx.author.mention}.")

    @commands.command(cls=utils.Command)
    @utils.checks.is_guild_moderator()
    @commands.guild_only()
    async def warn(self, ctx:utils.Context, user:discord.Member, *, reason:str):
        """Adds a warning to a user"""

        # Throw the reason into the database
        self.bot.dispatch("moderation_action", moderator=ctx.author, user=user, reason=reason, action="Warn")

        # Warn the user
        return await ctx.send(f"{user.mention} has been warned by {ctx.author.mention} with reason `{reason}`.")

    @commands.command(cls=utils.Command)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Kicks a user from the server"""

        # Check the user can run the command on who they want
        if user.top_role.position >= ctx.author.top_role.position:
            return await ctx.send("That user is too highly ranked for you to be able to punish them.")
        if user.top_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send("That user is too highly ranked for me to be able to punish them.")

        # DM the user
        dm_reason = f"You have been kicked from **{ctx.guild.name}** with the reason `{reason}`."
        try:
            await user.send(dm_reason)
        except discord.Forbidden:
            pass  # Can't DM the user? Oh well

        # Kick the user
        manage_reason = f"{ctx.author!s}: {reason}"
        try:
            await user.kick(reason=manage_reason)
        except discord.Forbidden:
            return await ctx.send(f"I was unable to kick {user.mention}.")
        except discord.NotFound:
            return await ctx.send("To me it looks like that user doesn't exist :/")

        # Throw the reason into the database
        self.bot.dispatch("moderation_action", moderator=ctx.author, user=user, reason=reason, action="Kick")

        # Output to chat
        return await ctx.send(f"{user.mention} has been kicked by {ctx.author.mention} with reason `{reason}`.")

    @commands.command(cls=utils.Command)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx:utils.Context, user:typing.Union[discord.Member, int], *, reason:str='<No reason provided>'):
        """Bans a user from the server"""

        # Do some setup here for users not in the server
        if isinstance(user, int):
            user_in_guild = False
            user = discord.Object(user)
        else:
            user_in_guild = True

        # Check the user can run the command on who they want
        if user_in_guild and user.top_role.position >= user.top_role.position:
            return await ctx.send("That user is too highly ranked for you to be able to punish them.")
        if user_in_guild and user.top_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send("That user is too highly ranked for me to be able to punish them.")

        # DM the user
        if user_in_guild:
            dm_reason = f"You have been kicked from **{ctx.guild.name}** with the reason `{reason}`."
            try:
                await user.send(dm_reason)
            except discord.Forbidden:
                pass  # Can't DM the user? Oh well

        # Kick the user
        manage_reason = f"{ctx.author!s}: {reason}"
        try:
            await ctx.guild.ban(user, reason=manage_reason)
        except discord.Forbidden:
            return await ctx.send(f"I was unable to ban {user.mention}.")
        except discord.NotFound:
            return await ctx.send("To me it looks like that user doesn't exist :/")

        # Throw the reason into the database
        self.bot.dispatch("moderation_action", moderator=ctx.author, user=user, reason=reason, action="Ban")

        # Output to chat
        await ctx.send(f"{user.mention} has been banned by {ctx.author.mention} with reason `{reason}`.")


def setup(bot:utils.Bot):
    x = ModerationCommands(bot)
    bot.add_cog(x)

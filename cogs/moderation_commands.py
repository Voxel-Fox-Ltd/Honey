import string
import random
from datetime import datetime as dt

import discord
from discord.ext import commands
from cogs import utils


class ModerationCommands(utils.Cog):

    async def get_code(self, db, n:int=5) -> str:
        """This method creates a randomisied string to use as the infraction identifier.

        Input Argument: n - Must be int
        Returns: A string n long
        """

        def gen_code(n):
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

        while True:
            code = gen_code(n)
            is_valid = await db("SELECT infraction_id FROM infractions WHERE infraction_id=$1", code)
            if len(is_valid) == 0:
                return code

    @commands.command(cls=utils.Command)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Mutes a user from the server"""

        # Check if role exists
        muted_role_id = self.bot.guild_settings[ctx.guild_id].get("muted_role_id")
        if muted_role_id is None:
            return await ctx.send("You have no mute role set.")

        # Grab the mute role
        mute_role = ctx.guild.get_role(muted_role_id)
        if mute_role is None:
            return await ctx.send("You have no mute role set.")
        if mute_role in user.roles:
            return await ctx.send(f"{user.mention} is already muted.")

        # Throw the reason into the database
        async with self.bot.database() as db:
            code = await self.get_code(db)
            await db(
                """INSERT INTO infractions (infraction_id, guild_id, user_id, moderator_id, infraction_type,
                infraction_reason, timestamp) VALUES ($1, $2, 'Mute', $3, $4)""",
                code, ctx.guild.id, user.id, ctx.author.id, reason, dt.utcnow(),
            )

        # Mute the user
        await user.add_roles(mute_role, reason=reason)
        with utils.Embed() as embed:
            embed.title = "Muted indefinitely!"
            embed.description = f"{user.mention} has been muted by {ctx.author.mention} with reason `{reason}`."
        return await ctx.send(embed=embed)

    @commands.command(cls=utils.Command)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx:utils.Context, user:discord.Member):
        """Unmutes a user"""

        # Check if role exists
        muted_role_id = self.bot.guild_settings[ctx.guild_id].get("muted_role_id")
        if muted_role_id is None:
            return await ctx.send("You have no mute role set.")

        # Grab the mute role
        mute_role = ctx.guild.get_role(muted_role_id)
        if mute_role is None:
            return await ctx.send("You have no mute role set.")
        if mute_role not in user.roles:
            return await ctx.send(f"{user.mention} is not muted.")

        # Unmute the user
        await user.remove_roles(mute_role)
        with utils.Embed() as embed:
            embed.title = "Unmuted!"
            embed.description = f"{user.mention} has been unmuted by {ctx.author.mention}."
        return await ctx.send(embed=embed)

    @commands.command(cls=utils.Command)
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Adds a warning to a user"""

        # Throw the reason into the database
        async with self.bot.database() as db:
            code = await self.get_code(db)
            await db(
                """INSERT INTO infractions (infraction_id, guild_id, user_id, moderator_id, infraction_type,
                infraction_reason, timestamp) VALUES ($1, $2, 'Warn', $3, $4)""",
                code, ctx.guild.id, user.id, ctx.author.id, reason, dt.utcnow(),
            )

        # Warn the user
        with utils.Embed() as embed:
            embed.title = "Warning Given",
            embed.description = f"{user.mention} has been warned by {ctx.author.mention} with reason `{reason}`."
        await ctx.send(embed=embed)

    @commands.command(cls=utils.Command)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Kicks a user from the server"""

        # Throw the reason into the database
        async with self.bot.database() as db:
            code = await self.get_code(db)
            await db(
                """INSERT INTO infractions (infraction_id, guild_id, user_id, moderator_id, infraction_type,
                infraction_reason, timestamp) VALUES ($1, $2, 'Kick', $3, $4)""",
                code, ctx.guild.id, user.id, ctx.author.id, reason, dt.utcnow(),
            )

        # Kick the user
        await ctx.guild.kick(user, reason=reason)
        with utils.Embed() as embed:
            embed.title = "Kicked!"
            embed.description = f"{user.mention} has been kicked by {ctx.author.mention} with reason `{reason}`."
        await ctx.send(embed=embed)

    @commands.command(cls=utils.Command)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Bans a user from the server"""

        # Throw the reason into the database
        async with self.bot.database() as db:
            code = await self.get_code(db)
            await db(
                """INSERT INTO infractions (infraction_id, guild_id, user_id, moderator_id, infraction_type,
                infraction_reason, timestamp) VALUES ($1, $2, 'Ban', $3, $4)""",
                code, ctx.guild.id, user.id, ctx.author.id, reason, dt.utcnow(),
            )

        # Ban the user
        await ctx.guild.ban(user, reason, delete_message_days=7)
        with utils.Embed() as embed:
            embed.title = "Banned!"
            embed.description = f"{user.mention} has been banned by {ctx.author.mention} with reason `{reason}`."
        await ctx.send(embed=embed)


def setup(bot:utils.Bot):
    x = ModerationCommands(bot)
    bot.add_cog(x)

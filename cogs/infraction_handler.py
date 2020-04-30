import string
import random
from datetime import datetime as dt

import discord
from discord.ext import commands
from discord.ext import menus

from cogs import utils


class InfractionSource(menus.ListPageSource):

    def format_page(self, menu:menus.Menu, entries:list) -> utils.Embed:
        """Format the infraction entries into an embed"""

        with utils.Embed(use_random_colour=True) as embed:
            for row in entries:
                # TODO add timestamp
                embed.add_field(f"{row['infraction_type']} - {row['infraction_id']}", f"<@{row['moderator_id']}> :: {row['infraction_reason']}", inline=False)
            embed.set_footer(f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return embed


class InfractionHandler(utils.Cog):

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
    async def on_moderation_action(self, moderator:discord.Member, user:discord.User, reason:str, action:str):
        """Looks for moderator actions being done and logs them into the relevant channel"""

        # Save to database
        db_reason = None if reason == '<No reason provided>' else reason
        async with self.bot.database() as db:
            code = await self.get_unused_infraction_id(db)
            await db(
                """INSERT INTO infractions (infraction_id, guild_id, user_id, moderator_id, infraction_type,
                infraction_reason, timestamp) VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                code, moderator.guild.id, user.id, moderator.id, action, db_reason, dt.utcnow(),
            )

        # Get log channel
        log_channel_id = self.bot.guild_settings[moderator.guild.id].get(f"{action.lower()}_modlog_channel_id", None)
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

    @commands.group(cls=utils.Group, invoke_without_command=True)
    @utils.checks.is_guild_moderator()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def infractions(self, ctx:utils.Context, user:discord.Member):
        """The parent to be able to see user infractions"""

        # Make sure there was no subcommand invoked
        if ctx.invoked_subcommand is not None:
            return

        # Grab their infractions from the database
        async with self.bot.database() as db:
            rows = await db("SELECT * FROM infractions WHERE guild_id=$1 AND user_id=$2 AND deleted_by IS NULL ORDER BY timestamp DESC", ctx.guild.id, user.id)
        if not rows:
            return await ctx.send(f"{user.mention} has no recorded infractions.")

        # And pagination time babey
        pages = menus.MenuPages(source=InfractionSource(rows, per_page=5), clear_reactions_after=True, delete_message_after=True)
        await pages.start(ctx)

    @infractions.command(cls=utils.Command)
    @utils.checks.is_guild_moderator()
    @commands.bot_has_permissions(send_messages=True)
    async def delete(self, ctx:utils.Context, infraction_id:str):
        """Delete an infraction given its ID"""

        # Grab their infractions from the database
        async with self.bot.database() as db:
            rows = await db("SELECT * FROM infractions WHERE LOWER(infraction_id)=LOWER($1) AND deleted_by IS NULL", infraction_id)
            await db("UPDATE infractions SET deleted_by=$2 WHERE LOWER(infraction_id)=LOWER($1)", infraction_id, ctx.author.id)
        if not rows:
            return await ctx.send(f"The ID you gave doesn't refer to an undeleted infraction.")
        return await ctx.send(f"Deleted infraction from <@{rows[0]['user_id']}>'s account.")

    @utils.Cog.listener()
    async def on_message_edit(self, before:discord.Message, after:discord.Message):
        """Logs edited messages"""

        # Filter
        if after.guild is None:
            return
        if before.content == after.content:
            return
        if not before.content or not after.content:
            return
        if after.author.bot:
            return

        # Create embed
        with utils.Embed(use_random_colour=True) as embed:
            embed.set_author_to_user(user=after.author)
            embed.description = f"[Message edited]({after.jump_url}) in {after.channel.mention}"
            before_content = before.content
            if len(before.content) > 1000:
                before_content = before.content[:1000] + '...'
            after_content = after.content
            if len(after.content) > 1000:
                after_content = after.content[:1000] + '...'
            embed.add_field(name="Old Message", value=before_content, inline=False)
            embed.add_field(name="New Message", value=after_content, inline=False)
            embed.timestamp = after.edited_at

        # Get channel
        channel_id = self.bot.guild_settings[after.guild.id].get("edited_message_modlog_channel_id")
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            return

        # Send log
        try:
            m = await channel.send(embed=embed)
            self.logger.info(f"Logging edited message (G{m.guild.id}/C{m.channel.id})")
        except discord.Forbidden:
            pass

    @utils.Cog.listener()
    async def on_message_delete(self, message:discord.Message):
        """Logs edited messages"""

        # Filter
        if message.guild is None:
            return
        if not message.content:
            return
        if message.author.bot:
            return

        # Create embed
        with utils.Embed(use_random_colour=True) as embed:
            embed.set_author_to_user(user=message.author)
            embed.description = f"Message deleted in {message.channel.mention}"
            if len(message.content) > 1000:
                embed.add_field(name="Message", value=message.content[:1000] + '...', inline=False)
            else:
                embed.add_field(name="Message", value=message.content, inline=False)
            embed.timestamp = dt.utcnow()

        # Get channel
        channel_id = self.bot.guild_settings[message.guild.id].get("deleted_message_modlog_channel_id")
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            return

        # Send log
        try:
            m = await channel.send(embed=embed)
            self.logger.info(f"Logging deleted message (G{m.guild.id}/C{m.channel.id})")
        except discord.Forbidden:
            pass


def setup(bot:utils.Bot):
    x = InfractionHandler(bot)
    bot.add_cog(x)

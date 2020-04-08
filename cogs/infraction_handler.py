import string
import random
from datetime import datetime as dt

import discord
from discord.ext import commands

from cogs import utils


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

    # @commands.group(cls=utils.Group)
    # @commands.
    # async def infractions(self, ctx:utils.Context):


def setup(bot:utils.Bot):
    x = InfractionHandler(bot)
    bot.add_cog(x)

import asyncpg
import discord
from discord.ext import commands

from cogs import utils


class BotSettings(utils.Cog):

    @commands.command(cls=utils.Command)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def prefix(self, ctx:utils.Context, *, new_prefix:str):
        """Changes the prefix that the bot uses"""

        # Validate prefix
        if len(new_prefix) > 30:
            return await ctx.send(f"The maximum length a prefix can be is 30 characters.")

        # Store setting
        self.bot.guild_settings[ctx.guild.id]['prefix'] = new_prefix
        async with self.bot.database() as db:
            try:
                await db("INSERT INTO guild_settings (guild_id, prefix) VALUES ($1, $2)", ctx.guild.id, new_prefix)
            except asyncpg.UniqueViolationError:
                await db("UPDATE guild_settings SET prefix=$2 WHERE guild_id=$1", ctx.guild.id, new_prefix)
        await ctx.send(f"My prefix has been updated to `{new_prefix}`.")

    @commands.command(cls=utils.Command)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def setchannel(self, ctx:utils.Context, key:str, channel:discord.TextChannel=None):
        """Changes the prefix that the bot uses"""

        # Make sure the key exists
        valid_keys = [
            'verified_role_id',
            'fursona_modmail_channel_id',
            'fursona_decline_archive_channel_id',
            'fursona_accept_archive_channel_id',
            'fursona_accept_nsfw_archive_channel_id',
        ]
        if key.lower() not in valid_keys:
            return await ctx.send("That isn't a valid key.")

        # Save to db
        key = key.lower()
        channel = channel or ctx.channel
        async with self.bot.database() as db:
            await db(f"INSERT INTO guild_settings (guild_id, {key}) VALUES ($1, $2)", ctx.guild.id, channel.id)
        self.bot.guild_settings[ctx.guild.id][key] = channel.id
        return await ctx.send("Updated guild settings.")


def setup(bot:utils.Bot):
    x = BotSettings(bot)
    bot.add_cog(x)

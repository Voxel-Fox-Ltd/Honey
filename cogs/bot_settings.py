import asyncio

import asyncpg
import discord
from discord.ext import commands

from cogs import utils


class MentionableNone(object):

    def __init__(self, mention_text:str="None"):
        self.mention_text = mention_text

    @property
    def mention(self):
        return self.mention_text


class BotSettings(utils.Cog):

    TICK_EMOJI = "<:tickYes:596096897995899097>"

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
    @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True, manage_messages=True, external_emojis=True)
    async def setup(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        message = None
        while True:

            # Construct embed
            guild_settings = self.bot.guild_settings[ctx.guild.id]
            with utils.Embed() as embed:
                embed.description = '\n'.join([
                    "1\N{COMBINING ENCLOSING KEYCAP} Set verified role (currently {0.mention})".format(ctx.guild.get_role(guild_settings.get("verified_role_id")) or MentionableNone("none")),
                    "2\N{COMBINING ENCLOSING KEYCAP} Set fursona modmail channel (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("fursona_modmail_channel_id")) or MentionableNone("none")),
                    "3\N{COMBINING ENCLOSING KEYCAP} Set fursona decline archive (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("fursona_decline_archive_channel_id")) or MentionableNone("none")),
                    "4\N{COMBINING ENCLOSING KEYCAP} Set fursona accept archive (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("fursona_accept_archive_channel_id")) or MentionableNone("none")),
                    "5\N{COMBINING ENCLOSING KEYCAP} Set NSFW fursona accept archive (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("fursona_accept_nsfw_archive_channel_id")) or MentionableNone("none")),
                    "6\N{COMBINING ENCLOSING KEYCAP} Set mod action archive (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("modmail_channel_id")) or MentionableNone("none")),
                    "7\N{COMBINING ENCLOSING KEYCAP} Set mute role (currently {0.mention})".format(ctx.guild.get_role(guild_settings.get("muted_role_id")) or MentionableNone("none")),
                    "8\N{COMBINING ENCLOSING KEYCAP} Set custom role master (currently {0.mention})".format(ctx.guild.get_role(guild_settings.get("custom_role_id")) or MentionableNone("none")),
                    "9\N{COMBINING ENCLOSING KEYCAP} Set custom role position (currently {0.mention})".format(ctx.guild.get_role(guild_settings.get("custom_role_position_id")) or MentionableNone("none")),
                ])

            # Send embed
            if message is None:
                message = await ctx.send(embed=embed)
                for i in range(1, embed.description.count('\n') + 2):
                    await message.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")
                await message.add_reaction(self.TICK_EMOJI)
            else:
                await message.edit(embed=embed)

            # Wait for added reaction
            emoji_key_map = {
                "1\N{COMBINING ENCLOSING KEYCAP}": ("verified_role_id", commands.RoleConverter, None),
                "2\N{COMBINING ENCLOSING KEYCAP}": ("fursona_modmail_channel_id", commands.TextChannelConverter, None),
                "3\N{COMBINING ENCLOSING KEYCAP}": ("fursona_decline_archive_channel_id", commands.TextChannelConverter, None),
                "4\N{COMBINING ENCLOSING KEYCAP}": ("fursona_accept_archive_channel_id", commands.TextChannelConverter, None),
                "5\N{COMBINING ENCLOSING KEYCAP}": ("fursona_accept_nsfw_archive_channel_id", commands.TextChannelConverter, None),
                "6\N{COMBINING ENCLOSING KEYCAP}": ("modmail_channel_id", commands.TextChannelConverter, None),
                "7\N{COMBINING ENCLOSING KEYCAP}": ("muted_role_id", commands.RoleConverter, None),
                "8\N{COMBINING ENCLOSING KEYCAP}": ("custom_role_id", commands.RoleConverter, "+Users with this role are able to make/manage their own custom role name and colour."),
                "9\N{COMBINING ENCLOSING KEYCAP}": ("custom_role_position_id", commands.RoleConverter, "+Give a role that newly created custom roles will be created _under_."),
                self.TICK_EMOJI: None,
            }
            def check(r, u):
                return u.id == ctx.author.id and r.message.id == message.id and str(r.emoji) in emoji_key_map.keys()
            try:
                r, _ = await self.bot.wait_for("reaction_add", check=check, timeout=120)
            except asyncio.TimeoutError:
                return await ctx.send("Timed out setting up bot.")

            # See what our key is
            emoji = str(r.emoji)
            key = emoji_key_map[emoji]
            if key is None:
                try:
                    await message.clear_reactions()
                except discord.HTTPException:
                    pass
                return await ctx.send("Alright, done setting up!")

            # Try and remove their reaction
            try:
                await message.remove_reaction(r, ctx.author)
            except discord.Forbidden:
                pass

            # And do some settin up
            v = await self.set_data(ctx, key[0], key[1], prompt=key[2])
            if v is None:
                return

    async def set_data(self, ctx:utils.Context, key:str, converter:commands.Converter, *, prompt:str=None):
        """Sets the datapoint for a key given its converter and index"""

        # Ask the user what they want to update to
        if prompt and prompt[0] == '+':
            prompt = "What do you want to update this value to? " + prompt[1:]
        prompt = prompt or "What do you want to update this value to?"
        bot_message = await ctx.send(prompt)
        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id
        try:
            user_message = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Timed out setting up bot.")
            return None

        # Let's try updating it
        try:
            value = await converter().convert(ctx, user_message.content)
        except commands.CommandError:
            try:
                await bot_message.delete()
            except discord.NotFound:
                pass
            try:
                await user_message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass
            return True

        # Save to db
        async with self.bot.database() as db:
            await db(f"INSERT INTO guild_settings (guild_id, {key}) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET {key}=excluded.{key}", ctx.guild.id, value.id)
        self.bot.guild_settings[ctx.guild.id][key] = value.id

        # Delete messasges
        try:
            await bot_message.delete()
        except discord.NotFound:
            pass
        try:
            await user_message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass
        return True

def setup(bot:utils.Bot):
    x = BotSettings(bot)
    bot.add_cog(x)

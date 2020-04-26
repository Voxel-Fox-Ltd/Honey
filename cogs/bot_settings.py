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
    PLUS_EMOJI = "\N{HEAVY PLUS SIGN}"

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

    @commands.group(cls=utils.Group, aliases=['settings'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True, manage_messages=True, external_emojis=True)
    async def setup(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        if ctx.invoked_subcommand is not None:
            return

        message = None
        while True:

            # Construct embed
            with utils.Embed() as embed:
                embed.description = '\n'.join([
                    "1\N{COMBINING ENCLOSING KEYCAP} Set up channels",
                    "2\N{COMBINING ENCLOSING KEYCAP} Set up roles",
                    "3\N{COMBINING ENCLOSING KEYCAP} Set up interaction cooldowns",
                    "4\N{COMBINING ENCLOSING KEYCAP} Set up max sona counts",
                    "5\N{COMBINING ENCLOSING KEYCAP} Misc settings",
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
                "1\N{COMBINING ENCLOSING KEYCAP}": "setup channels",
                "2\N{COMBINING ENCLOSING KEYCAP}": "setup roles",
                "3\N{COMBINING ENCLOSING KEYCAP}": "setup interactions",
                "4\N{COMBINING ENCLOSING KEYCAP}": "setup sonacount",
                "5\N{COMBINING ENCLOSING KEYCAP}": "setup misc",
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
                    await message.delete()
                except discord.HTTPException:
                    pass
                return await ctx.send("Alright, done setting up!")

            # Try and remove their reaction
            try:
                await message.remove_reaction(r, ctx.author)
            except discord.Forbidden:
                pass

            # And do some settin up
            command = self.bot.get_command(key)
            ctx.invoke_meta = True
            await command.invoke(ctx)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def channels(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        message = None
        while True:

            # Construct embed
            guild_settings = self.bot.guild_settings[ctx.guild.id]
            with utils.Embed() as embed:
                embed.description = '\n'.join([
                    "1\N{COMBINING ENCLOSING KEYCAP} Set fursona modmail channel (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("fursona_modmail_channel_id")) or MentionableNone("none")),
                    "2\N{COMBINING ENCLOSING KEYCAP} Set fursona decline archive (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("fursona_decline_archive_channel_id")) or MentionableNone("none")),
                    "3\N{COMBINING ENCLOSING KEYCAP} Set fursona accept archive (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("fursona_accept_archive_channel_id")) or MentionableNone("none")),
                    "4\N{COMBINING ENCLOSING KEYCAP} Set NSFW fursona accept archive (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("fursona_accept_nsfw_archive_channel_id")) or MentionableNone("none")),
                    "5\N{COMBINING ENCLOSING KEYCAP} Set mod action archive (currently {0.mention})".format(self.bot.get_channel(guild_settings.get("modmail_channel_id")) or MentionableNone("none")),
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
                "1\N{COMBINING ENCLOSING KEYCAP}": ("fursona_modmail_channel_id", commands.TextChannelConverter, None),
                "2\N{COMBINING ENCLOSING KEYCAP}": ("fursona_decline_archive_channel_id", commands.TextChannelConverter, None),
                "3\N{COMBINING ENCLOSING KEYCAP}": ("fursona_accept_archive_channel_id", commands.TextChannelConverter, None),
                "4\N{COMBINING ENCLOSING KEYCAP}": ("fursona_accept_nsfw_archive_channel_id", commands.TextChannelConverter, None),
                "5\N{COMBINING ENCLOSING KEYCAP}": ("modmail_channel_id", commands.TextChannelConverter, None),
                self.TICK_EMOJI: None,
            }
            def check(r, u):
                return u.id == ctx.author.id and r.message.id == message.id and str(r.emoji) in emoji_key_map.keys()
            try:
                r, _ = await self.bot.wait_for("reaction_add", check=check, timeout=120)
            except asyncio.TimeoutError:
                return await ctx.send("Timed out setting up database.")

            # See what our key is
            emoji = str(r.emoji)
            key = emoji_key_map[emoji]
            if key is None:
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                return

            # Try and remove their reaction
            try:
                await message.remove_reaction(r, ctx.author)
            except discord.Forbidden:
                pass

            # And do some settin up
            v = await self.set_data_in_guild_settings(ctx, key[0], key[1], prompt=key[2])
            if v is None:
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                return

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def roles(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        message = None
        while True:

            # Construct embed
            guild_settings = self.bot.guild_settings[ctx.guild.id]
            with utils.Embed() as embed:
                embed.description = '\n'.join([
                    "1\N{COMBINING ENCLOSING KEYCAP} Set verified role (currently {0.mention})".format(ctx.guild.get_role(guild_settings.get("verified_role_id")) or MentionableNone("none")),
                    "2\N{COMBINING ENCLOSING KEYCAP} Set mute role (currently {0.mention})".format(ctx.guild.get_role(guild_settings.get("muted_role_id")) or MentionableNone("none")),
                    "3\N{COMBINING ENCLOSING KEYCAP} Set roles removed on mute (currently {0})".format(len(guild_settings.get("removed_on_mute_roles", set()))),
                    "4\N{COMBINING ENCLOSING KEYCAP} Set moderator role (currently {0.mention})".format(ctx.guild.get_role(guild_settings.get("guild_moderator_role_id")) or MentionableNone("none")),
                    "5\N{COMBINING ENCLOSING KEYCAP} Set custom role master (currently {0.mention})".format(ctx.guild.get_role(guild_settings.get("custom_role_id")) or MentionableNone("none")),
                    "6\N{COMBINING ENCLOSING KEYCAP} Set custom role position (currently {0.mention})".format(ctx.guild.get_role(guild_settings.get("custom_role_position_id")) or MentionableNone("none")),
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
                "2\N{COMBINING ENCLOSING KEYCAP}": ("muted_role_id", commands.RoleConverter, None),
                "3\N{COMBINING ENCLOSING KEYCAP}": ("setup removeroles",),
                "4\N{COMBINING ENCLOSING KEYCAP}": ("guild_moderator_role_id", commands.RoleConverter, None),
                "5\N{COMBINING ENCLOSING KEYCAP}": ("custom_role_id", commands.RoleConverter, "+Users with this role are able to make/manage their own custom role name and colour."),
                "6\N{COMBINING ENCLOSING KEYCAP}": ("custom_role_position_id", commands.RoleConverter, "+Give a role that newly created custom roles will be created _under_."),
                self.TICK_EMOJI: None,
            }
            def check(r, u):
                return u.id == ctx.author.id and r.message.id == message.id and str(r.emoji) in emoji_key_map.keys()
            try:
                r, _ = await self.bot.wait_for("reaction_add", check=check, timeout=120)
            except asyncio.TimeoutError:
                return await ctx.send("Timed out setting up database.")

            # See what our key is
            emoji = str(r.emoji)
            key = emoji_key_map[emoji]
            if key is None:
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                return

            # Try and remove their reaction
            try:
                await message.remove_reaction(r, ctx.author)
            except discord.Forbidden:
                pass

            # And do some settin up
            if len(key) > 1:
                v = await self.set_data_in_guild_settings(ctx, key[0], key[1], prompt=key[2])
                if v is None:
                    try:
                        await message.delete()
                    except discord.HTTPException:
                        pass
                    return
            else:
                command = self.bot.get_command(key[0])
                ctx.invoke_meta = True
                await command.invoke(ctx)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def interactions(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        message = None
        while True:

            # Construct embed
            role_settings = self.bot.guild_settings[ctx.guild.id].get("role_interaction_cooldowns", dict())
            with utils.Embed() as embed:
                role_emoji = []
                description = ["@everyone - 30m"]
                for i, o in role_settings.items():
                    role = ctx.guild.get_role(i)
                    if role is None:
                        continue
                    text = f"{len(role_emoji) + 1}\N{COMBINING ENCLOSING KEYCAP} {role.mention} - {utils.TimeValue(o).clean}"
                    description.append(text)
                    role_emoji.append((f"{len(role_emoji) + 1}\N{COMBINING ENCLOSING KEYCAP}", role))
                embed.description = '\n'.join(description)

            # Send embed
            if message is None:
                message = await ctx.send(embed=embed)
            else:
                await message.edit(embed=embed)
                await message.clear_reactions()
            for i in range(1, embed.description.count('\n') + 1):
                await message.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")
            await message.add_reaction(self.PLUS_EMOJI)
            await message.add_reaction(self.TICK_EMOJI)

            # Wait for added reaction
            emoji_key_map = {
                self.PLUS_EMOJI: False,
                self.TICK_EMOJI: None,
            }
            emoji_key_map.update({i:o for i, o in role_emoji})
            def check(r, u):
                return u.id == ctx.author.id and r.message.id == message.id and str(r.emoji) in emoji_key_map.keys()
            try:
                r, _ = await self.bot.wait_for("reaction_add", check=check, timeout=120)
            except asyncio.TimeoutError:
                return await ctx.send("Timed out setting up database.")

            # See what our key is
            emoji = str(r.emoji)
            key = emoji_key_map[emoji]
            if key is None:
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                return

            # Try and remove their reaction
            try:
                await message.remove_reaction(r, ctx.author)
            except discord.Forbidden:
                pass

            # They wanna delete a role
            if isinstance(key, discord.Role):
                del self.bot.guild_settings[ctx.guild.id]['role_interaction_cooldowns'][role.id]
                async with self.bot.database() as db:
                    await db("DELETE FROM role_list WHERE guild_id=$1 AND role_id=$2 AND key='Interactions'", ctx.guild.id, role.id)
                continue

            # They wanna add a new role
            if key is False:
                new_role = await self.ask_for_information(ctx, "What role do you want to add?", "role", commands.RoleConverter)
                if new_role is None:
                    continue
                cooldown_time: utils.TimeValue = await self.ask_for_information(ctx, "How long should the cooldown for this role be (eg 5m)?", "duration", utils.TimeValue)
                if cooldown_time is None:
                    continue
                async with self.bot.database() as db:
                    await db(
                        """INSERT INTO role_list (guild_id, role_id, key, value) VALUES ($1, $2, 'Interactions', $3)
                        ON CONFLICT (guild_id, role_id, key) DO UPDATE SET value=excluded.value""",
                        ctx.guild.id, new_role.id, str(cooldown_time.duration)
                    )
                self.bot.guild_settings[ctx.guild.id]['role_interaction_cooldowns'][new_role.id] = cooldown_time.duration

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def removeroles(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        message = None
        while True:

            # Construct embed
            role_settings = self.bot.guild_settings[ctx.guild.id].get("removed_on_mute_roles", list())
            with utils.Embed() as embed:
                role_emoji = []
                description = []
                for i in role_settings:
                    role = ctx.guild.get_role(i)
                    if role is None:
                        continue
                    text = f"{len(role_emoji) + 1}\N{COMBINING ENCLOSING KEYCAP} {role.mention}"
                    description.append(text)
                    role_emoji.append((f"{len(role_emoji) + 1}\N{COMBINING ENCLOSING KEYCAP}", role))
                embed.description = '\n'.join(description) or "No roles set up"

            # Send embed
            if message is None:
                message = await ctx.send(embed=embed)
            else:
                await message.edit(embed=embed)
                await message.clear_reactions()
            if '@' in embed.description:
                for i in range(1, len(role_settings) + 1):
                    await message.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")
            await message.add_reaction(self.PLUS_EMOJI)
            await message.add_reaction(self.TICK_EMOJI)

            # Wait for added reaction
            emoji_key_map = {
                self.PLUS_EMOJI: False,
                self.TICK_EMOJI: None,
            }
            emoji_key_map.update({i:o for i, o in role_emoji})
            def check(r, u):
                return u.id == ctx.author.id and r.message.id == message.id and str(r.emoji) in emoji_key_map.keys()
            try:
                r, _ = await self.bot.wait_for("reaction_add", check=check, timeout=120)
            except asyncio.TimeoutError:
                return await ctx.send("Timed out setting up database.")

            # See what our key is
            emoji = str(r.emoji)
            key = emoji_key_map[emoji]
            if key is None:
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                return

            # Try and remove their reaction
            try:
                await message.remove_reaction(r, ctx.author)
            except discord.Forbidden:
                pass

            # They wanna delete a role
            if isinstance(key, discord.Role):
                self.bot.guild_settings[ctx.guild.id]['removed_on_mute_roles'].remove(role.id)
                async with self.bot.database() as db:
                    await db("DELETE FROM role_list WHERE guild_id=$1 AND role_id=$2 AND key='RemoveOnMute'", ctx.guild.id, role.id)
                continue

            # They wanna add a new role
            if key is False:
                new_role = await self.ask_for_information(ctx, "What role do you want to add?", "role", commands.RoleConverter)
                if new_role is None:
                    continue
                async with self.bot.database() as db:
                    await db(
                        """INSERT INTO role_list (guild_id, role_id, key) VALUES ($1, $2, 'RemoveOnMute')""",
                        ctx.guild.id, new_role.id
                    )
                self.bot.guild_settings[ctx.guild.id]['removed_on_mute_roles'].append(new_role.id)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def sonacount(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        message = None
        while True:

            # Construct embed
            role_settings = self.bot.guild_settings[ctx.guild.id].get("role_sona_count", dict())
            with utils.Embed() as embed:
                role_emoji = []
                description = ["@everyone - 1 sona"]
                for i, o in role_settings.items():
                    role = ctx.guild.get_role(i)
                    if role is None:
                        continue
                    text = f"{len(role_emoji) + 1}\N{COMBINING ENCLOSING KEYCAP} {role.mention} - {o} sonas"
                    description.append(text)
                    role_emoji.append((f"{len(role_emoji) + 1}\N{COMBINING ENCLOSING KEYCAP}", role))
                embed.description = '\n'.join(description)

            # Send embed
            if message is None:
                message = await ctx.send(embed=embed)
            else:
                await message.edit(embed=embed)
                await message.clear_reactions()
            for i in range(1, embed.description.count('\n') + 1):
                await message.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")
            await message.add_reaction(self.PLUS_EMOJI)
            await message.add_reaction(self.TICK_EMOJI)

            # Wait for added reaction
            emoji_key_map = {
                self.PLUS_EMOJI: False,
                self.TICK_EMOJI: None,
            }
            emoji_key_map.update({i:o for i, o in role_emoji})
            def check(r, u):
                return u.id == ctx.author.id and r.message.id == message.id and str(r.emoji) in emoji_key_map.keys()
            try:
                r, _ = await self.bot.wait_for("reaction_add", check=check, timeout=120)
            except asyncio.TimeoutError:
                return await ctx.send("Timed out setting up database.")

            # See what our key is
            emoji = str(r.emoji)
            key = emoji_key_map[emoji]
            if key is None:
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                return

            # Try and remove their reaction
            try:
                await message.remove_reaction(r, ctx.author)
            except discord.Forbidden:
                pass

            # They wanna delete a role
            if isinstance(key, discord.Role):
                del self.bot.guild_settings[ctx.guild.id]['role_sona_count'][role.id]
                async with self.bot.database() as db:
                    await db("DELETE FROM role_list WHERE guild_id=$1 AND role_id=$2 AND key='SonaCount'", ctx.guild.id, role.id)
                continue

            # They wanna add a new role
            if key is False:
                new_role = await self.ask_for_information(ctx, "What role do you want to add?", "role", commands.RoleConverter)
                if new_role is None:
                    continue
                sona_amount: int = await self.ask_for_information(ctx, "How many sonas can people with this role create?", "integer", int)
                if sona_amount is None:
                    continue
                async with self.bot.database() as db:
                    await db(
                        """INSERT INTO role_list (guild_id, role_id, key, value) VALUES ($1, $2, 'SonaCount', $3)
                        ON CONFLICT (guild_id, role_id, key) DO UPDATE SET value=excluded.value""",
                        ctx.guild.id, new_role.id, str(sona_amount)
                    )
                self.bot.guild_settings[ctx.guild.id]['role_sona_count'][new_role.id] = sona_amount

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def misc(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        message = None
        while True:

            # Construct embed
            guild_settings = self.bot.guild_settings[ctx.guild.id]
            with utils.Embed() as embed:
                embed.description = '\n'.join([
                    "1\N{COMBINING ENCLOSING KEYCAP} Set coin emoji (currently `{0}`)".format(guild_settings.get("coin_emoji") or " coins"),
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
                "1\N{COMBINING ENCLOSING KEYCAP}": ("coin_emoji", str, "What do you want to set the coin emoji to? This appears when users run the coins command."),
                self.TICK_EMOJI: None,
            }
            def check(r, u):
                return u.id == ctx.author.id and r.message.id == message.id and str(r.emoji) in emoji_key_map.keys()
            try:
                r, _ = await self.bot.wait_for("reaction_add", check=check, timeout=120)
            except asyncio.TimeoutError:
                return await ctx.send("Timed out setting up misc.")

            # See what our key is
            emoji = str(r.emoji)
            key = emoji_key_map[emoji]
            if key is None:
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                return

            # Try and remove their reaction
            try:
                await message.remove_reaction(r, ctx.author)
            except discord.Forbidden:
                pass

            # And do some settin up
            v = await self.set_data_in_guild_settings(ctx, key[0], key[1], prompt=key[2], attrs=[])
            if v is None:
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                return

    async def ask_for_information(self, ctx:utils.Context, prompt:str, asking_for:str, converter:commands.Converter):
        """Ask for some user information babeyeyeyeyyeyeyeye"""

        # Send message
        bot_message = await ctx.send(prompt)
        check = lambda m: m.channel.id == ctx.channel.id and m.author.id == ctx.author.id
        try:
            user_message = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f"Timed out asking for {asking_for}.")
            return None

        # Convert the user's message
        if hasattr(converter, 'convert'):
            # if isinstance(converter, commands.Converter):
            try:
                converter = converter()
            except TypeError:
                pass
            try:
                value = await converter.convert(ctx, user_message.content)
            except commands.CommandError:
                value = None
        else:
            try:
                value = converter(user_message.content)
            except Exception:
                value = None

        # Delete messages
        try:
            await bot_message.delete()
        except discord.NotFound:
            pass
        try:
            await user_message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass
        return value

    async def set_data_in_guild_settings(self, ctx:utils.Context, key:str, converter:commands.Converter, *, prompt:str=None, attrs:list=['id']):
        """Sets the datapoint for a key given its converter and index"""

        # Ask the user what they want to update to
        converter_type = {
            commands.RoleConverter: "role",
            commands.TextChannelConverter: "channel"
        }.get(converter, "value")
        if prompt and prompt[0] == '+':
            prompt = f"What do you want to set this {converter_type} to? " + prompt[1:]
        prompt = prompt or f"What do you want to set this {converter_type} to?"

        # Ask the user
        value = await self.ask_for_information(ctx, prompt, converter_type, converter)
        if value is None:
            return True

        # Get our attrs from the value
        set_value = value
        for i in attrs:
            set_value = getattr(set_value, i)

        # Save to db
        async with self.bot.database() as db:
            await db(f"INSERT INTO guild_settings (guild_id, {key}) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET {key}=excluded.{key}", ctx.guild.id, set_value)
        self.bot.guild_settings[ctx.guild.id][key] = set_value
        return True


def setup(bot:utils.Bot):
    x = BotSettings(bot)
    bot.add_cog(x)

import operator

import discord
from discord.ext import commands
import voxelbotutils as vbu


class BotSettings(vbu.Cog):

    TICK_EMOJI = "\N{HEAVY CHECK MARK}"
    CROSS_EMOJI = "\N{HEAVY MULTIPLICATION X}"

    @vbu.group()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True, manage_messages=True)
    @commands.guild_only()
    async def setup(self, ctx: vbu.Context):
        """
        Run the bot setup.
        """

        # Make sure it's only run as its own command, not a parent
        if ctx.invoked_subcommand is not None:
            return

        menu = vbu.SettingsMenu()
        menu.add_multiple_options(
            vbu.SettingsMenuOption(
                ctx=ctx,
                display="Custom role settings",
                callback=self.bot.get_command("setup customroles"),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display="Moderation settings",
                callback=self.bot.get_command("setup moderation"),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display="Fursona settings",
                callback=self.bot.get_command("setup fursonas"),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display="Interaction cooldowns",
                callback=self.bot.get_command("setup interactions"),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display="Shop settings",
                callback=self.bot.get_command("setup shop"),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display="Command disabling",
                callback=self.bot.get_command("setup botcommands"),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display="Misc settings",
                callback=self.bot.get_command("setup misc"),
            ),
        )
        try:
            await menu.start(ctx)
            await ctx.send("Done setting up!")
        except vbu.errors.InvokedMetaCommand:
            pass

    @setup.command()
    @vbu.checks.meta_command()
    async def fursonas(self, ctx: vbu.Context):
        """
        Fursonas submenu.
        """

        menu = vbu.SettingsMenu()
        settings_mention = vbu.SettingsMenuOption.get_guild_settings_mention
        menu.add_multiple_options(
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Allow NSFW fursonas (currently {0})".format(settings_mention(c, 'nsfw_is_allowed')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="Do you want to allow NSFW fursonas?",
                        asking_for="allow NSFW",
                        converter=vbu.converters.BooleanConverter,
                        emojis=[self.TICK_EMOJI, self.CROSS_EMOJI],
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'nsfw_is_allowed'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set fursona modmail channel (currently {0})".format(settings_mention(c, 'fursona_modmail_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want to set fursona modmail to go to?",
                        asking_for="fursona modmail",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'fursona_modmail_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set fursona decline archive channel (currently {0})".format(settings_mention(c, 'fursona_decline_archive_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want declined fursonas to go to?",
                        asking_for="fursona decline archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'fursona_decline_archive_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set fursona accept archive channel (currently {0})".format(settings_mention(c, 'fursona_accept_archive_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want accepted fursonas to go to?",
                        asking_for="fursona accept archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'fursona_accept_archive_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set NSFW fursona accept archive channel (currently {0})".format(settings_mention(c, 'fursona_accept_nsfw_archive_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want accepted NSFW fursonas to go to?",
                        asking_for="NSFW fursona accept archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'fursona_accept_nsfw_archive_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display="Set max sona counts by role",
                callback=self.bot.get_command("setup sonacount"),
            ),
        )
        await menu.start(ctx)

    @setup.command()
    @vbu.checks.meta_command()
    async def shop(self, ctx: vbu.Context):
        """
        Shop submenu.
        """

        menu = vbu.SettingsMenu()
        settings_mention = vbu.SettingsMenuOption.get_guild_settings_mention
        menu.add_multiple_options(
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set paintbrush price (currently {0})".format(settings_mention(c, 'paintbrush_price')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="How much do you want a paintbrush to cost? Set to 0 to disable paint being sold on the shop.",
                        asking_for="paint price",
                        converter=int,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'paintbrush_price'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set cooldown token price (currently {0})".format(settings_mention(c, 'cooldown_token_price')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="How much do you want 100 cooldown tokens to cost? Set to 0 to disable cooldown tokens being sold on the shop.",
                        asking_for="paint price",
                        converter=int,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'cooldown_token_price'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set up buyable roles (currently {0} set up)".format(len(c.bot.guild_settings[c.guild.id].get('buyable_roles', list()))),
                callback=self.bot.get_command("setup buyableroles"),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set up buyable temporary roles (currently {0} set up)".format(len(c.bot.guild_settings[c.guild.id].get('buyable_temporary_roles', list()))),
                callback=self.bot.get_command("setup buyabletemproles"),
            ),
        )
        await menu.start(ctx)
        self.bot.dispatch("shop_message_update", ctx.guild)

    @setup.command()
    @vbu.checks.meta_command()
    async def buyableroles(self, ctx: vbu.Context):
        """
        Buyable roles setup.
        """

        menu = vbu.SettingsMenuIterable(
            table_name="role_list",
            column_name="role_id",
            cache_key="buyable_roles",
            database_key="BuyableRoles",
            key_display_function=lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none'),
            converters=[
                vbu.SettingsMenuConverter(
                    prompt="What role would you like to add to the shop?",
                    asking_for="role",
                    converter=commands.RoleConverter,
                ),
                vbu.SettingsMenuConverter(
                    prompt="How much should the role cost?",
                    asking_for="role price",
                    converter=int,
                ),
            ]
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @vbu.checks.meta_command()
    async def buyabletemproles(self, ctx: vbu.Context):
        """
        Buyable roles setup.
        """

        def add_callback(menu: vbu.SettingsMenu, ctx: vbu.Context):
            async def callback(menu: vbu.SettingsMenu, role: discord.Role, price: int, duration: vbu.TimeValue):
                async with ctx.bot.database() as db:
                    await db(
                        """INSERT INTO buyable_temporary_roles (guild_id, role_id, price, duration) VALUES ($1, $2, $3, $4)
                        ON CONFLICT (guild_id, role_id) DO UPDATE SET price=excluded.price, duration=excluded.duration""",
                        role.guild.id, role.id, price, duration.duration
                    )
                ctx.bot.guild_settings[ctx.guild.id]['buyable_temporary_roles'][role.id] = {'price': price, 'duration': duration.duration}
            return callback

        def delete_callback(menu: vbu.SettingsMenu, ctx: vbu.Context, role_id: int):
            async def callback(menu: vbu.SettingsMenu):
                async with ctx.bot.database() as db:
                    await db(
                        """DELETE FROM buyable_temporary_roles WHERE guild_id=$1 AND role_id=$2""",
                        ctx.guild.id, role_id
                    )
                ctx.bot.guild_settings[ctx.guild.id]['buyable_temporary_roles'].pop(role_id)
            return callback

        menu = vbu.SettingsMenuIterable(
            table_name="buyable_temporary_roles",
            column_name="role_id",
            cache_key="buyable_temporary_roles",
            database_key="BuyableRoles",
            key_display_function=lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none'),
            value_display_function=lambda v: f"{v['price']} for {vbu.TimeValue(v['duration']).clean}",
            converters=[
                vbu.SettingsMenuConverter(
                    prompt="What role would you like to add to the shop?",
                    asking_for="role",
                    converter=commands.RoleConverter,
                ),
                vbu.SettingsMenuConverter(
                    prompt="How much should the role cost?",
                    asking_for="role price",
                    converter=int,
                ),
                vbu.SettingsMenuConverter(
                    prompt="How long should this role's cooldown be (eg `5m`, `15s`, etc)?",
                    asking_for="role duration",
                    converter=vbu.TimeValue,
                ),
            ],
            iterable_add_callback=add_callback,
            iterable_delete_callback=delete_callback,
        )

        await menu.start(ctx, clear_reactions_on_loop=True)
        self.bot.dispatch("shop_message_update", ctx.guild)

    @setup.command()
    @vbu.checks.meta_command()
    async def customroles(self, ctx: vbu.Context):
        """
        Custom roles setup.
        """

        menu = vbu.SettingsMenu()
        settings_mention = vbu.SettingsMenuOption.get_guild_settings_mention
        menu.add_multiple_options(
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set custom role master (currently {0})".format(settings_mention(c, 'custom_role_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What do you want to set this role to? Users with this role are able to make/manage their own custom role name and colour.",
                        asking_for="custom role master",
                        converter=commands.RoleConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'custom_role_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set custom role position (currently below {0})".format(settings_mention(c, 'custom_role_position_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What do you want to set this role to? Give a role that newly created custom roles will be created _under_.",
                        asking_for="custom role position",
                        converter=commands.RoleConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'custom_role_position_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set custom role name xfix (currently `{0}`)".format(c.bot.guild_settings[c.guild.id].get('custom_role_xfix', None) or ':(Custom)'),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What do you want your custom role suffix to be? If your name ends with a colon (eg `(Custom):`) then it'll be added to the role as a prefix rather than a suffix.",
                        asking_for="custom role suffix",
                        converter=str,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'custom_role_xfix'),
            ),
        )
        await menu.start(ctx)

    @setup.command()
    @vbu.checks.meta_command()
    async def moderation(self, ctx: vbu.Context):
        """
        Moderation setup.
        """

        # Make sure it's only run as its own command, not a parent
        if ctx.invoked_subcommand is not None:
            return

        # Create settings menu
        menu = vbu.SettingsMenu()
        settings_mention = vbu.SettingsMenuOption.get_guild_settings_mention
        menu.add_multiple_options(
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set verified role (currently {0})".format(settings_mention(c, 'verified_role_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What do you want to set the verified role to?",
                        asking_for="verified role",
                        converter=commands.RoleConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'verified_role_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set mute role (currently {0})".format(settings_mention(c, 'muted_role_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What do you want to set the mute role to?",
                        asking_for="mute role",
                        converter=commands.RoleConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'muted_role_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set roles which are removed on mute (currently {0})".format(len(c.bot.guild_settings[c.guild.id].get('removed_on_mute_roles', []))),
                callback=self.bot.get_command("setup removerolesonmute"),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set moderator role (currently {0})".format(settings_mention(c, 'guild_moderator_role_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What do you want to set the moderator role to?",
                        asking_for="moderator role",
                        converter=commands.RoleConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'guild_moderator_role_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display="Set moderator action archive channels",
                callback=self.bot.get_command("setup modlogs"),
            ),
        )
        await menu.start(ctx)

    @setup.command()
    @vbu.checks.meta_command()
    async def modlogs(self, ctx: vbu.Context):
        """
        Modlogs setup.
        """

        menu = vbu.SettingsMenu()
        settings_mention = vbu.SettingsMenuOption.get_guild_settings_mention
        menu.add_multiple_options(
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set kick archive channel (currently {0})".format(settings_mention(c, 'kick_modlog_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want kicks to be logged to?",
                        asking_for="kicked users archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'kick_modlog_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set ban archive channel (currently {0})".format(settings_mention(c, 'ban_modlog_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want bans to be logged to?",
                        asking_for="banned users archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'ban_modlog_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set mute archive channel (currently {0})".format(settings_mention(c, 'mute_modlog_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want mutes to be logged to?",
                        asking_for="muted users archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'mute_modlog_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set warn archive channel (currently {0})".format(settings_mention(c, 'warn_modlog_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want warns to be logged to?",
                        asking_for="warned users archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'warn_modlog_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set edited message archive channel (currently {0})".format(settings_mention(c, 'edited_message_modlog_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want edited message logs to be logged to?",
                        asking_for="edited message archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'edited_message_modlog_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set deleted message archive channel (currently {0})".format(settings_mention(c, 'deleted_message_modlog_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want deleted message logs to go to?",
                        asking_for="deleted message archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'deleted_message_modlog_channel_id'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set voice update log channel (currently {0})".format(settings_mention(c, 'voice_update_modlog_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What channel do you want user voice state updates to be logged to?",
                        asking_for="VC update archive",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'voice_update_modlog_channel_id'),
            ),
        )
        await menu.start(ctx)

    @setup.command()
    @vbu.checks.meta_command()
    async def interactions(self, ctx: vbu.Context):
        """
        Interactions setup.
        """

        menu = vbu.SettingsMenuIterable(
            table_name="role_list",
            column_name="role_id",
            cache_key="role_interaction_cooldowns",
            database_key="Interactions",
            key_display_function=lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none'),
            converters=[
                vbu.SettingsMenuConverter(
                    prompt="What role do you want to set the interaction for?",
                    asking_for="role",
                    converter=commands.RoleConverter,
                ),
                vbu.SettingsMenuConverter(
                    prompt="How long should this role's cooldown be (eg `5m`, `15s`, etc)?",
                    asking_for="role cooldown",
                    converter=vbu.TimeValue,
                    serialize_function=operator.attrgetter("duration"),
                ),
            ]
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @vbu.checks.meta_command()
    async def botcommands(self, ctx: vbu.Context):
        """
        Bot command blacklisting setup.
        """

        menu = vbu.SettingsMenu()
        menu.add_multiple_options(
            vbu.SettingsMenuOption(
                ctx=ctx,
                display='Disable sona commands for channels',
                callback=self.bot.get_command('setup disablesona')
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display='Disable interaction commands for channels',
                callback=self.bot.get_command('setup disableinteractions')
            ),
        )
        await menu.start(ctx)

    @setup.command()
    @vbu.checks.meta_command()
    async def disablesona(self, ctx: vbu.Context):
        """
        Sona channel disable setup.
        """

        menu = vbu.SettingsMenuIterable(
            table_name="channel_list",
            column_name="channel_id",
            cache_key="disabled_sona_channels",
            database_key="DisabledSonaChannel",
            key_display_function=lambda k: getattr(ctx.guild.get_channel(k), 'mention', 'none'),
            converters=[
                vbu.SettingsMenuConverter(
                    prompt="What channel you want the sona command to be disabled in?",
                    asking_for="channel",
                    converter=commands.TextChannelConverter,
                ),
            ]
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @vbu.checks.meta_command()
    async def disableinteractions(self, ctx: vbu.Context):
        """
        Interaction channel disable setup.
        """

        menu = vbu.SettingsMenuIterable(
            table_name="channel_list",
            column_name="channel_id",
            cache_key="disabled_interaction_channels",
            database_key="DisabledInteractionChannel",
            key_display_function=lambda k: getattr(ctx.guild.get_channel(k), 'mention', 'none'),
            converters=[
                vbu.SettingsMenuConverter(
                    prompt="What channel you want the interaction commands to be disabled in?",
                    asking_for="channel",
                    converter=commands.TextChannelConverter,
                ),
            ]
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @vbu.checks.meta_command()
    async def removerolesonmute(self, ctx: vbu.Context):
        """
        Role remove on mute.
        """

        menu = vbu.SettingsMenuIterable(
            table_name="role_list",
            column_name="role_id",
            cache_key="removed_on_mute_roles",
            database_key="RemoveOnMute",
            key_display_function=lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none'),
            converters=[
                vbu.SettingsMenuConverter(
                    prompt="What role do you want to be removed on mute?",
                    asking_for="role",
                    converter=commands.RoleConverter,
                ),
            ]
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @vbu.checks.meta_command()
    async def sonacount(self, ctx: vbu.Context):
        """
        Sona role count setup.
        """

        menu = vbu.SettingsMenuIterable(
            table_name="role_list",
            column_name="role_id",
            cache_key="role_sona_count",
            database_key="SonaCount",
            key_display_function=lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none'),
            converters=[
                vbu.SettingsMenuConverter(
                    prompt="What role do you want to set the sona count for?",
                    asking_for="role",
                    converter=commands.RoleConverter,
                ),
                vbu.SettingsMenuConverter(
                    prompt="How many sonas should people with this role be able to create?",
                    asking_for="sona count",
                    converter=int,
                ),
            ]
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @vbu.checks.meta_command()
    async def misc(self, ctx: vbu.Context):
        """
        Misc setup.
        """

        menu = vbu.SettingsMenu()
        settings_mention = vbu.SettingsMenuOption.get_guild_settings_mention
        menu.add_multiple_options(
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set coin emoji (currently {0})".format(settings_mention(c, 'coin_emoji', 'coins')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What do you want to set the coin emoji to?",
                        asking_for="coin emoji",
                        converter=str,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'coin_emoji'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Set suggestions channel (currently {0})".format(settings_mention(ctx, 'suggestion_channel_id')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="What do you want to set the suggestion channel to?",
                        asking_for="suggestion channel",
                        converter=commands.TextChannelConverter,
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'suggestion_channel_id'),
            ),
        )
        await menu.start(ctx)

    @commands.group()
    @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True)
    @vbu.cooldown.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def usersettings(self, ctx: vbu.Context):
        """
        User settings.
        """

        # Make sure it's only run as its own command, not a parent
        if ctx.invoked_subcommand is not None:
            return

        # Create settings menu
        menu = vbu.SettingsMenu()
        settings_mention = vbu.SettingsMenuOption.get_user_settings_mention
        menu.add_multiple_options(
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Receive DM on paint removal (currently {0})".format(settings_mention(c, 'dm_on_paint_remove')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="Do you want to receive a DM when paint is removed from you?",
                        asking_for="paint DM",
                        converter=vbu.converters.BooleanConverter,
                        emojis=[self.TICK_EMOJI, self.CROSS_EMOJI],
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'dm_on_paint_remove'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Allow paint from other users (currently {0})".format(settings_mention(c, 'allow_paint')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="Do you want to allow other users to paint you?",
                        asking_for="paint enable",
                        converter=vbu.converters.BooleanConverter,
                        emojis=[self.TICK_EMOJI, self.CROSS_EMOJI],
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'allow_paint'),
            ),
            vbu.SettingsMenuOption(
                ctx=ctx,
                display=lambda c: "Allow interaction pings (currently {0})".format(settings_mention(c, 'receive_interaction_ping')),
                converter_args=[
                    vbu.SettingsMenuConverter(
                        prompt="Do you want to be pinged when users run interactions on you?",
                        asking_for="interaction ping",
                        converter=vbu.converters.BooleanConverter,
                        emojis=[self.TICK_EMOJI, self.CROSS_EMOJI],
                    ),
                ],
                callback=vbu.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'receive_interaction_ping'),
            ),
        )
        try:
            await menu.start(ctx)
            await ctx.send("Done setting up!")
        except vbu.errors.InvokedMetaCommand:
            pass


def setup(bot: vbu.Bot):
    x = BotSettings(bot)
    bot.add_cog(x)

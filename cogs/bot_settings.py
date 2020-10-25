import discord
from discord.ext import commands
import voxelbotutils as utils


class BotSettings(utils.Cog):

    TICK_EMOJI = "\N{HEAVY CHECK MARK}"
    CROSS_EMOJI = "\N{HEAVY MULTIPLICATION X}"

    @utils.group()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True, manage_messages=True)
    @commands.guild_only()
    async def setup(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        if ctx.invoked_subcommand is not None:
            return

        menu = utils.SettingsMenu()
        menu.bulk_add_options(
            ctx,
            {
                'display': "Custom role settings",
                'callback': self.bot.get_command("setup customroles"),
            },
            {
                'display': "Moderation settings",
                'callback': self.bot.get_command("setup moderation"),
            },
            {
                'display': "Fursona settings",
                'callback': self.bot.get_command("setup fursonas"),
            },
            {
                'display': "Interaction cooldowns",
                'callback': self.bot.get_command("setup interactions"),
            },
            {
                'display': "Shop settings",
                'callback': self.bot.get_command("setup shop"),
            },
            {
                'display': "Command disabling",
                'callback': self.bot.get_command("setup botcommands"),
            },
            {
                'display': "Misc settings",
                'callback': self.bot.get_command("setup misc"),
            },
        )
        try:
            await menu.start(ctx)
            await ctx.send("Done setting up!")
        except utils.errors.InvokedMetaCommand:
            pass

    @setup.command()
    @utils.checks.meta_command()
    async def fursonas(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Allow NSFW fursonas (currently {0})".format(settings_mention(c, 'nsfw_is_allowed')),
                'converter_args': [("Do you want to allow NSFW fursonas?", "allow NSFW", utils.converters.BooleanConverter, [self.TICK_EMOJI, self.CROSS_EMOJI])],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'nsfw_is_allowed'),
            },
            {
                'display': lambda c: "Set fursona modmail channel (currently {0})".format(settings_mention(c, 'fursona_modmail_channel_id')),
                'converter_args': [("What channel do you want to set fursona modmail to go to?", "fursona modmail", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'fursona_modmail_channel_id'),
            },
            {
                'display': lambda c: "Set fursona decline archive channel (currently {0})".format(settings_mention(c, 'fursona_decline_archive_channel_id')),
                'converter_args': [("What channel do you want declined fursonas to go to?", "fursona decline archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'fursona_decline_archive_channel_id'),
            },
            {
                'display': lambda c: "Set fursona accept archive channel (currently {0})".format(settings_mention(c, 'fursona_accept_archive_channel_id')),
                'converter_args': [("What channel do you want accepted fursonas to go to?", "fursona accept archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'fursona_accept_archive_channel_id'),
            },
            {
                'display': lambda c: "Set NSFW fursona accept archive channel (currently {0})".format(settings_mention(c, 'fursona_accept_nsfw_archive_channel_id')),
                'converter_args': [("What channel do you want accepted NSFW fursonas to go to?", "NSFW fursona accept archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'fursona_accept_nsfw_archive_channel_id'),
            },
            {
                'display': "Set max sona counts by role",
                'callback': self.bot.get_command("setup sonacount"),
            },
        )
        await menu.start(ctx)

    @setup.command()
    @utils.checks.meta_command()
    async def shop(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Set paintbrush price (currently {0})".format(settings_mention(c, 'paintbrush_price')),
                'converter_args': [("How much do you want a paintbrush to cost? Set to 0 to disable paint being sold on the shop.", "paint price", int)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'paintbrush_price'),
            },
            {
                'display': lambda c: "Set cooldown token price (currently {0})".format(settings_mention(c, 'cooldown_token_price')),
                'converter_args': [("How much do you want 100 cooldown tokens to cost? Set to 0 to disable cooldown tokens being sold on the shop.", "paint price", int)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'cooldown_token_price'),
            },
            {
                'display': lambda c: "Set up buyable roles (currently {0} set up)".format(len(c.bot.guild_settings[c.guild.id].get('buyable_roles', list()))),
                'callback': self.bot.get_command("setup buyableroles"),
            },
            {
                'display': lambda c: "Set up buyable temporary roles (currently {0} set up)".format(len(c.bot.guild_settings[c.guild.id].get('buyable_temporary_roles', list()))),
                'callback': self.bot.get_command("setup buyabletemproles"),
            },
        )
        await menu.start(ctx)
        self.bot.dispatch("shop_message_update", ctx.guild)

    @setup.command()
    @utils.checks.meta_command()
    async def buyableroles(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        key_display_function = lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none')
        menu = utils.SettingsMenuIterableBase(cache_key='buyable_roles', key_display_function=key_display_function, value_display_function=str, default_type=dict)
        menu.add_convertable_value("What role would you like to add to the shop?", commands.RoleConverter)
        menu.add_convertable_value("How much should the role cost?", int)
        menu.iterable_add_callback = utils.SettingsMenuOption.get_set_iterable_add_callback(
            table_name="role_list", column_name="role_id", cache_key="buyable_roles", database_key="BuyableRoles"
        )
        menu.iterable_delete_callback = utils.SettingsMenuOption.get_set_iterable_delete_callback(
            table_name="role_list", column_name="role_id", cache_key="buyable_roles", database_key="BuyableRoles"
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @utils.checks.meta_command()
    async def buyabletemproles(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        key_display_function = lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none')
        menu = utils.SettingsMenuIterableBase(cache_key='buyable_temporary_roles', key_display_function=key_display_function, value_display_function=lambda v: f"{v['price']} for {utils.TimeValue(v['duration']).clean}", default_type=dict)
        menu.add_convertable_value("What role would you like to add to the shop?", commands.RoleConverter)
        menu.add_convertable_value("How much should the role cost?", int)
        menu.add_convertable_value("How long should this role's cooldown be (eg `5m`, `15s`, etc)?", utils.TimeValue)

        def add_callback(menu:utils.SettingsMenu, ctx:utils.Context):
            async def callback(menu:utils.SettingsMenu, role:discord.Role, price:int, duration:utils.TimeValue):
                async with ctx.bot.database() as db:
                    await db(
                        """INSERT INTO buyable_temporary_roles (guild_id, role_id, price, duration) VALUES ($1, $2, $3, $4)
                        ON CONFLICT (guild_id, role_id) DO UPDATE SET price=excluded.price, duration=excluded.duration""",
                        role.guild.id, role.id, price, duration.duration
                    )
                ctx.bot.guild_settings[ctx.guild.id]['buyable_temporary_roles'][role.id] = {'price': price, 'duration': duration.duration}
            return callback
        menu.iterable_add_callback = add_callback

        def delete_callback(menu:utils.SettingsMenu, ctx:utils.Context, role_id:int):
            async def callback(menu:utils.SettingsMenu):
                async with ctx.bot.database() as db:
                    await db(
                        """DELETE FROM buyable_temporary_roles WHERE guild_id=$1 AND role_id=$2""",
                        ctx.guild.id, role_id
                    )
                ctx.bot.guild_settings[ctx.guild.id]['buyable_temporary_roles'].pop(role_id)
            return callback
        menu.iterable_delete_callback = delete_callback

        await menu.start(ctx, clear_reactions_on_loop=True)
        self.bot.dispatch("shop_message_update", ctx.guild)

    @setup.command()
    @utils.checks.meta_command()
    async def customroles(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Set custom role master (currently {0})".format(settings_mention(c, 'custom_role_id')),
                'converter_args': [("What do you want to set this role to? Users with this role are able to make/manage their own custom role name and colour.", "verified role", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'custom_role_id'),
            },
            {
                'display': lambda c: "Set custom role position (currently below {0})".format(settings_mention(c, 'custom_role_position_id')),
                'converter_args': [("What do you want to set this role to? Give a role that newly created custom roles will be created _under_.", "custom role position", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'custom_role_position_id'),
            },
            {
                'display': lambda c: "Set custom role name xfix (currently `{0}`)".format(c.bot.guild_settings[c.guild.id].get('custom_role_xfix', None) or ':(Custom)'),
                'converter_args': [("What do you want your custom role suffix to be? If your name ends with a colon (eg `(Custom):`) then it'll be added to the role as a prefix rather than a suffix.", "custom role suffix", str)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'custom_role_xfix'),
            },
        )
        await menu.start(ctx)

    @setup.command()
    @utils.checks.meta_command()
    async def moderation(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        # Make sure it's only run as its own command, not a parent
        if ctx.invoked_subcommand is not None:
            return

        # Create settings menu
        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Set verified role (currently {0})".format(settings_mention(c, 'verified_role_id')),
                'converter_args': [("What do you want to set the verified role to?", "verified role", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'verified_role_id'),
            },
            {
                'display': lambda c: "Set mute role (currently {0})".format(settings_mention(c, 'muted_role_id')),
                'converter_args': [("What do you want to set the mute role to?", "mute role", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'muted_role_id'),
            },
            {
                'display': lambda c: "Set roles which are removed on mute (currently {0})".format(len(c.bot.guild_settings[c.guild.id].get('removed_on_mute_roles', []))),
                'callback': self.bot.get_command("setup removerolesonmute"),
            },
            {
                'display': lambda c: "Set moderator role (currently {0})".format(settings_mention(c, 'guild_moderator_role_id')),
                'converter_args': [("What do you want to set the moderator role to?", "moderator role", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'guild_moderator_role_id'),
            },
            {
                'display': "Set moderator action archive channels",
                'callback': self.bot.get_command("setup modlogs"),
            },
        )
        await menu.start(ctx)

    @setup.command()
    @utils.checks.meta_command()
    async def modlogs(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Set kick archive channel (currently {0})".format(settings_mention(c, 'kick_modlog_channel_id')),
                'converter_args': [("What channel do you want kicks to go to?", "modmail archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'kick_modlog_channel_id'),
            },
            {
                'display': lambda c: "Set ban archive channel (currently {0})".format(settings_mention(c, 'ban_modlog_channel_id')),
                'converter_args': [("What channel do you want bans to go to?", "modmail archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'ban_modlog_channel_id'),
            },
            {
                'display': lambda c: "Set mute archive channel (currently {0})".format(settings_mention(c, 'mute_modlog_channel_id')),
                'converter_args': [("What channel do you want mutes to go to?", "modmail archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'mute_modlog_channel_id'),
            },
            {
                'display': lambda c: "Set warn archive channel (currently {0})".format(settings_mention(c, 'warn_modlog_channel_id')),
                'converter_args': [("What channel do you want warns to go to?", "modmail archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'warn_modlog_channel_id'),
            },
            {
                'display': lambda c: "Set edited message archive channel (currently {0})".format(settings_mention(c, 'edited_message_modlog_channel_id')),
                'converter_args': [("What channel do you want edited message logs to go to?", "modmail archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'edited_message_modlog_channel_id'),
            },
            {
                'display': lambda c: "Set deleted message archive channel (currently {0})".format(settings_mention(c, 'deleted_message_modlog_channel_id')),
                'converter_args': [("What channel do you want deleted message logs to go to?", "modmail archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'deleted_message_modlog_channel_id'),
            },
            {
                'display': lambda c: "Set voice update log channel (currently {0})".format(settings_mention(c, 'voice_update_modlog_channel_id')),
                'converter_args': [("What channel do you want deleted message logs to go to?", "VC update archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'voice_update_modlog_channel_id'),
            },
        )
        await menu.start(ctx)

    @setup.command()
    @utils.checks.meta_command()
    async def interactions(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        key_display_function = lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none')
        menu = utils.SettingsMenuIterableBase(cache_key='role_interaction_cooldowns', key_display_function=key_display_function, value_display_function=lambda v: utils.TimeValue(v).clean, default_type=dict)
        menu.add_convertable_value("What role do you want to set the interaction for?", commands.RoleConverter)
        menu.add_convertable_value("How long should this role's cooldown be (eg `5m`, `15s`, etc)?", utils.TimeValue)
        menu.iterable_add_callback = utils.SettingsMenuOption.get_set_iterable_add_callback(
            table_name="role_list", column_name="role_id", cache_key="role_interaction_cooldowns", database_key="Interactions", serialize_function=lambda x: int(x.duration)
        )
        menu.iterable_delete_callback = utils.SettingsMenuOption.get_set_iterable_delete_callback(
            table_name="role_list", column_name="role_id", cache_key="role_interaction_cooldowns", database_key="Interactions"
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @utils.checks.meta_command()
    async def botcommands(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        menu.bulk_add_options(
            ctx,
            {
                'display': 'Disable sona commands for channels',
                'callback': self.bot.get_command('setup disablesona')
            },
            {
                'display': 'Disable interaction commands for channels',
                'callback': self.bot.get_command('setup disableinteractions')
            },
        )
        await menu.start(ctx)

    @setup.command()
    @utils.checks.meta_command()
    async def disablesona(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        key_display_function = lambda k: getattr(ctx.guild.get_channel(k), 'mention', 'none')
        menu = utils.SettingsMenuIterableBase(cache_key='disabled_sona_channels', key_display_function=key_display_function, value_display_function=str, default_type=list)
        menu.add_convertable_value("What channel you want the sona command to be disabled in?", commands.TextChannelConverter)
        menu.iterable_add_callback = utils.SettingsMenuOption.get_set_iterable_add_callback(
            table_name="channel_list", column_name="channel_id", cache_key="disabled_sona_channels", database_key="DisabledSonaChannel"
        )
        menu.iterable_delete_callback = utils.SettingsMenuOption.get_set_iterable_delete_callback(
            table_name="channel_list", column_name="channel_id", cache_key="disabled_sona_channels", database_key="DisabledSonaChannel"
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @utils.checks.meta_command()
    async def disableinteractions(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        key_display_function = lambda k: getattr(ctx.guild.get_channel(k), 'mention', 'none')
        menu = utils.SettingsMenuIterableBase(cache_key='disabled_interaction_channels', key_display_function=key_display_function, value_display_function=str, default_type=list)
        menu.add_convertable_value("What channel you want the interaction commands to be disabled in?", commands.TextChannelConverter)
        menu.iterable_add_callback = utils.SettingsMenuOption.get_set_iterable_add_callback(
            table_name="channel_list", column_name="channel_id", cache_key="disabled_interaction_channels", database_key="DisabledInteractionChannel"
        )
        menu.iterable_delete_callback = utils.SettingsMenuOption.get_set_iterable_delete_callback(
            table_name="channel_list", column_name="channel_id", cache_key="disabled_interaction_channels", database_key="DisabledInteractionChannel"
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @utils.checks.meta_command()
    async def removerolesonmute(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        key_display_function = lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none')
        menu = utils.SettingsMenuIterableBase(cache_key='removed_on_mute_roles', key_display_function=key_display_function, value_display_function=str, default_type=list)
        menu.add_convertable_value("What role do you want to be removed on mute?", commands.RoleConverter)
        menu.iterable_add_callback = utils.SettingsMenuOption.get_set_iterable_add_callback(
            table_name="role_list", column_name="role_id", cache_key="removed_on_mute_roles", database_key="RemoveOnMute"
        )
        menu.iterable_delete_callback = utils.SettingsMenuOption.get_set_iterable_delete_callback(
            table_name="role_list", column_name="role_id", cache_key="removed_on_mute_roles", database_key="RemoveOnMute"
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @utils.checks.meta_command()
    async def sonacount(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        key_display_function = lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none')
        menu = utils.SettingsMenuIterableBase(cache_key='role_sona_count', key_display_function=key_display_function, value_display_function=str, default_type=dict)
        menu.add_convertable_value("What role do you want to set the sona count for?", commands.RoleConverter)
        menu.add_convertable_value("How many sonas should people with this role be able to create?", int)
        menu.iterable_add_callback = utils.SettingsMenuOption.get_set_iterable_add_callback(
            table_name="role_list", column_name="role_id", cache_key="role_sona_count", database_key="SonaCount"
        )
        menu.iterable_delete_callback = utils.SettingsMenuOption.get_set_iterable_delete_callback(
            table_name="role_list", column_name="role_id", cache_key="role_sona_count", database_key="SonaCount"
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command()
    @utils.checks.meta_command()
    async def misc(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Set coin emoji (currently {0})".format(settings_mention(c, 'coin_emoji', 'coins')),
                'converter_args': [("What do you want to set the coin emoji to?", "coin emoji", str)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'coin_emoji'),
            },
            {
                'display': lambda c: "Set suggestions channel (currently {0})".format(settings_mention(ctx, 'suggestion_channel_id')),
                'converter_args': [("What do you want to set the suggestion channel to?", "suggestion channel", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'suggestion_channel_id'),
            },
        )
        await menu.start(ctx)

    @commands.group()
    @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True)
    @utils.cooldown.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def usersettings(self, ctx:utils.Context):
        """Run the bot setup"""

        # Make sure it's only run as its own command, not a parent
        if ctx.invoked_subcommand is not None:
            return

        # Create settings menu
        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_user_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Receive DM on paint removal (currently {0})".format(settings_mention(c, 'dm_on_paint_remove')),
                'converter_args': [("Do you want to receive a DM when paint is removed from you?", "paint DM", utils.converters.BooleanConverter, [self.TICK_EMOJI, self.CROSS_EMOJI])],
                'callback': utils.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'dm_on_paint_remove'),
            },
            {
                'display': lambda c: "Allow paint from other users (currently {0})".format(settings_mention(c, 'allow_paint')),
                'converter_args': [("Do you want to allow other users to paint you?", "paint enable", utils.converters.BooleanConverter, [self.TICK_EMOJI, self.CROSS_EMOJI])],
                'callback': utils.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'allow_paint'),
            },
            {
                'display': lambda c: "Allow interaction pings (currently {0})".format(settings_mention(c, 'receive_interaction_ping')),
                'converter_args': [("Do you want to be pinged when users run interactions on you?", "interaction ping", utils.converters.BooleanConverter, [self.TICK_EMOJI, self.CROSS_EMOJI])],
                'callback': utils.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'receive_interaction_ping'),
            },
        )
        try:
            await menu.start(ctx)
            await ctx.send("Done setting up!")
        except utils.errors.InvokedMetaCommand:
            pass


def setup(bot:utils.Bot):
    x = BotSettings(bot)
    bot.add_cog(x)

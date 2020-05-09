from discord.ext import commands

from cogs import utils


class BotSettings(utils.Cog):

    TICK_EMOJI = "<:tickYes:596096897995899097>"
    CROSS_EMOJI = "<:crossNo:596096897769275402>"

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
            await db("INSERT INTO guild_settings (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix=excluded.prefix", ctx.guild.id, new_prefix)
        await ctx.send(f"My prefix has been updated to `{new_prefix}`.")

    @commands.group(cls=utils.Group)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True, manage_messages=True, external_emojis=True)
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
                'display': "Misc settings",
                'callback': self.bot.get_command("setup misc"),
            },
        )
        await menu.start(ctx)
        await ctx.send("Done with setup!")

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def fursonas(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
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

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def shop(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Set paint price (currently {0})".format(settings_mention(c, 'paint_price')),
                'converter_args': [("How much do you want paint to cost? Set to 0 to disable paint being sold on the shop.", "paint price", int)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_shop_settings', 'paint_price'),
            },
        )
        await menu.start(ctx)

    @setup.command(cls=utils.Command)
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

    @setup.command(cls=utils.Command)
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

    @setup.command(cls=utils.Command)
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
        )
        await menu.start(ctx)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def interactions(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenuIterable(
            'role_interaction_cooldowns', 'Interactions',
            commands.RoleConverter, "What role do you want to set the interaction for?",
            utils.TimeValue, "How long should this role's cooldown be (eg `5m`, `15s`, etc)?",
            lambda x: int(x.duration)
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def removerolesonmute(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenuIterable(
            'removed_on_mute_roles', 'RemoveOnMute',
            commands.RoleConverter, "What role do you want to be removed on mute?",
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def sonacount(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenuIterable(
            'role_sona_count', 'SonaCount',
            commands.RoleConverter, "What role do you want to set the sona count for?",
            int, "How many sonas should people with this role be able to create?",
        )
        await menu.start(ctx, clear_reactions_on_loop=True)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def misc(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Set coin emoji (currently {0})".format(c.bot.guild_settings[c.guild.id].get('coin_emoji', 'coins')),
                'converter_args': [("What do you want to set the coin emoji to?", "coin emoji", str)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'coin_emoji'),
            },
        )
        try:
            await menu.start(ctx)
            await ctx.send("Done setting up!")
        except utils.errors.InvokedMetaCommand:
            pass

    @commands.group(cls=utils.Group)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @utils.cooldown.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def usersettings(self, ctx:utils.Context):
        """Run the bot setup"""

        # Make sure it's only run as its own command, not a parent
        if ctx.invoked_subcommand is not None:
            return

        # Create settings menu
        menu = utils.SettingsMenu()
        # settings_mention = utils.SettingsMenuOption.get_user_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Do you want to be DMd on paint removal (currently {0})".format(c.bot.user_settings[c.author.id].get('dm_on_paint_remove', True)),
                'converter_args': [("Do you want to receive a DM when paint is removed from you?", "paint DM", utils.converters.BooleanConverter, [self.TICK_EMOJI, self.CROSS_EMOJI])],
                'callback': utils.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'dm_on_paint_remove'),
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

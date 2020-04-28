import asyncio

import discord
from discord.ext import commands

from cogs import utils


class BotSettings(utils.Cog):

    TICK_EMOJI = "<:tickYes:596096897995899097>"
    PLUS_EMOJI = "\N{HEAVY PLUS SIGN}"

    @commands.group(cls=utils.Group, aliases=['settings'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True, manage_messages=True, external_emojis=True)
    async def setup(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        if ctx.invoked_subcommand is not None:
            return

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': "Channel settings",
                'callback': self.bot.get_command("setup channels"),
            },
            {
                'display': "Role settings",
                'callback': self.bot.get_command("setup roles"),
            },
            {
                'display': "Interaction Cooldowns",
                'callback': self.bot.get_command("setup interactions"),
            },
            {
                'display': "Max Sona Counts",
                'callback': self.bot.get_command("setup sonacount"),
            },
            {
                'display': "Misc settings",
                'callback': self.bot.get_command("setup misc"),
            },
        )
        await menu.start(ctx)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def channels(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Set fursona modmail channel (currently {0})".format(settings_mention(c, 'fursona_modmail_channel_id')),
                'converter_args': [("What channel do you want to set fursona modmail to go to?", "fursona modmail", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('fursona_modmail_channel_id'),
            },
            {
                'display': lambda c: "Set fursona decline archive channel (currently {0})".format(settings_mention(c, 'fursona_decline_archive_channel_id')),
                'converter_args': [("What channel do you want declined fursonas to go to?", "fursona decline archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('fursona_decline_archive_channel_id'),
            },
            {
                'display': lambda c: "Set fursona accept archive channel (currently {0})".format(settings_mention(c, 'fursona_accept_archive_channel_id')),
                'converter_args': [("What channel do you want accepted fursonas to go to?", "fursona accept archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('fursona_accept_archive_channel_id'),
            },
            {
                'display': lambda c: "Set NSFW fursona accept archive channel (currently {0})".format(settings_mention(c, 'fursona_accept_nsfw_archive_channel_id')),
                'converter_args': [("What channel do you want accepted NSFW fursonas to go to?", "NSFW fursona accept archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('fursona_accept_nsfw_archive_channel_id'),
            },
            {
                'display': lambda c: "Set moderator action archive channel (currently {0})".format(settings_mention(c, 'modmail_channel_id')),
                'converter_args': [("What channel do you want moderator actions (like kicks/mutes, etc) to go to?", "modmail archive", commands.TextChannelConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('modmail_channel_id'),
            },
        )
        await menu.start(ctx)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def roles(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenu()
        settings_mention = utils.SettingsMenuOption.get_guild_settings_mention
        menu.bulk_add_options(
            ctx,
            {
                'display': lambda c: "Set verified role (currently {0})".format(settings_mention(c, 'verified_role_id')),
                'converter_args': [("What do you want to set the verified role to?", "verified role", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('verified_role_id'),
            },
            {
                'display': lambda c: "Set mute role (currently {0})".format(settings_mention(c, 'muted_role_id')),
                'converter_args': [("What do you want to set the mute role to?", "mute role", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('muted_role_id'),
            },
            {
                'display': lambda c: "Set roles which are removed on mute (currently {0})".format(len(c.bot.guild_settings[c.guild.id].get('removed_on_mute_roles', []))),
                'callback': self.bot.get_command("setup removerolesonmute"),
            },
            {
                'display': lambda c: "Set moderator role (currently {0})".format(settings_mention(c, 'guild_moderator_role_id')),
                'converter_args': [("What do you want to set the moderator role to?", "moderator role", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('guild_moderator_role_id'),
            },
            {
                'display': lambda c: "Set custom role master (currently {0})".format(settings_mention(c, 'custom_role_id')),
                'converter_args': [("What do you want to set this role to? Users with this role are able to make/manage their own custom role name and colour.", "verified role", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('custom_role_id'),
            },
            {
                'display': lambda c: "Set custom role position (currently below {0})".format(settings_mention(c, 'custom_role_position_id')),
                'converter_args': [("What do you want to set this role to? Give a role that newly created custom roles will be created _under_.", "custom role position", commands.RoleConverter)],
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('custom_role_position_id'),
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
            lambda x: x.duration
        )
        await menu.start(ctx)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def removerolesonmute(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenuIterable(
            'removed_on_mute_roles', 'RemoveOnMute',
            commands.RoleConverter, "What role do you want to be removed on mute?",
        )
        await menu.start(ctx)

    @setup.command(cls=utils.Command)
    @utils.checks.meta_command()
    async def sonacount(self, ctx:utils.Context):
        """Talks the bot through a setup"""

        menu = utils.SettingsMenuIterable(
            'role_sona_count', 'SonaCount',
            commands.RoleConverter, "What role do you want to set the sona count for?",
            int, "How many sonas should people with this role be able to create?",
        )
        await menu.start(ctx)

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
                'callback': utils.SettingsMenuOption.get_set_guild_settings_callback('coin_emoji'),
            },
        )
        await menu.start(ctx)


def setup(bot:utils.Bot):
    x = BotSettings(bot)
    bot.add_cog(x)

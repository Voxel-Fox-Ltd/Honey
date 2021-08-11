import discord
from discord.ext import commands
import voxelbotutils as vbu


settings_menu = vbu.menus.Menu(
    vbu.menus.Option(
        display="Custom role settings",
        callback=vbu.menus.Menu(
            vbu.menus.Option(
                display=lambda ctx: f"Custom role master (currently {ctx.get_mentionable_role(ctx.bot.guild_settings[ctx.guild.id]['custom_role_id']).mention})",
                component_display="Set custom role master",
                converters=[
                    vbu.menus.Converter(
                        prompt="What role do you want to set as the requirement for people to create custom roles?",
                        converter=discord.Role,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "custom_role_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "custom_role_id"),
            ),
            vbu.menus.Option(
                display=lambda ctx: f"Custom role position master (currently {ctx.get_mentionable_role(ctx.bot.guild_settings[ctx.guild.id]['custom_role_position_id']).mention})",
                component_display="Set custom role position",
                converters=[
                    vbu.menus.Converter(
                        prompt="What do you want to set this role to? Give a role that newly created custom roles will be created *under*.",
                        converter=discord.Role,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "custom_role_position_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "custom_role_position_id"),
            ),
            vbu.menus.Option(
                display=lambda ctx: "Custom role name xfix (currently `{0}`)".format(ctx.bot.guild_settings[ctx.guild.id].get('custom_role_xfix', None) or ':(Custom)'),
                component_display="Set custom role xfix",
                converters=[
                    vbu.menus.Converter(
                        prompt="What do you want your custom role suffix to be? If your name ends with a colon (eg `(Custom):`) then it'll be added to the role as a prefix rather than a suffix.",
                        converter=str,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "custom_role_xfix"),
                cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "custom_role_xfix"),
            ),
        ),
    ),
    vbu.menus.Option(
        display="Moderation settings",
        callback=vbu.menus.Menu(
            vbu.menus.Option(
                display=lambda ctx: f"Verified role (currently {ctx.get_mentionable_role(ctx.bot.guild_settings[ctx.guild.id]['verified_role_id']).mention})",
                component_display="Set verified role",
                converters=[
                    vbu.menus.Converter(
                        prompt="What do you want to set the verified role to?",
                        converter=discord.Role,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "verified_role_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "verified_role_id"),
            ),
            vbu.menus.Option(
                display=lambda ctx: f"Mute role (currently {ctx.get_mentionable_role(ctx.bot.guild_settings[ctx.guild.id]['muted_role_id']).mention})",
                component_display="Set mute role",
                converters=[
                    vbu.menus.Converter(
                        prompt="What do you want to set the mute role to?",
                        converter=discord.Role,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "muted_role_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "muted_role_id"),
            ),
            vbu.menus.Option(
                display=lambda ctx: f"Moderator role (currently {ctx.get_mentionable_role(ctx.bot.guild_settings[ctx.guild.id]['guild_moderator_role_id'])})",
                component_display="Set moderator role",
                converters=[
                    vbu.menus.Converter(
                        prompt="What do you want to set the moderator role to?",
                        converter=discord.Role,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "guild_moderator_role_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "guild_moderator_role_id"),
            ),
            vbu.menus.Option(
                display="Roles removed on mute",
                component_display="Set roles removed on mute",
                callback=vbu.menus.MenuIterable(
                    select_sql="SELECT * FROM role_list WHERE guild_id=$1 AND key='RemoveOnMute'",
                    select_sql_args=lambda ctx: (ctx.guild.id,),
                    insert_sql="INSERT INTO role_list (guild_id, role_id, key) VALUES ($1, $2, 'RemoveOnMute')",
                    insert_sql_args=lambda ctx, data: (ctx.guild.id, data[0].id,),
                    delete_sql="DELETE FROM role_list WHERE guild_id=$1 AND role_id=$2 AND key='RemoveOnMute'",
                    delete_sql_args=lambda ctx, row: (ctx.guild.id, row['role_id'],),
                    row_text_display=lambda ctx, row: ctx.get_mentionable_role(row['role_id']).mention,
                    row_component_display=lambda ctx, row: ctx.get_mentionable_role(row['role_id']).name,
                    converters=[
                        vbu.menus.Converter(
                            prompt="What role do you want to be removed when a user is muted?",
                            converter=discord.Role,
                        ),
                    ],
                    cache_callback=vbu.menus.Menu.callbacks.set_iterable_list_cache(vbu.menus.DataLocation.GUILD, "guild_settings", "removed_on_mute_roles"),
                    cache_delete_callback=vbu.menus.Menu.callbacks.delete_iterable_list_cache(vbu.menus.DataLocation.GUILD, "guild_settings", "removed_on_mute_roles"),
                    cache_delete_args=lambda row: (row['role_id'],)
                ),

            ),
            vbu.menus.Option(
                display="Action archive channels",
                component_display="Set action archive channels",
                callback=vbu.menus.Menu(
                    vbu.menus.Option(
                        display=lambda ctx: f"Kick log channel ({ctx.get_mentionable_channel(ctx).mention})",
                        component_display="Set kick log channel",
                        converters=[
                            vbu.menus.Converter(
                                prompt="What would you like to set the kick log channel to?",
                                converter=discord.TextChannel,
                            ),
                        ],
                        callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "kick_modlog_channel_id"),
                        cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "guild_settings", "kick_modlog_channel_id"),
                        allow_none=True,
                    ),
                    vbu.menus.Option(
                        display=lambda ctx: f"Ban log channel ({ctx.get_mentionable_channel(ctx).mention})",
                        component_display="Set ban log channel",
                        converters=[
                            vbu.menus.Converter(
                                prompt="What would you like to set the ban log channel to?",
                                converter=discord.TextChannel,
                            ),
                        ],
                        callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "ban_modlog_channel_id"),
                        cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "guild_settings", "ban_modlog_channel_id"),
                        allow_none=True,
                    ),
                    vbu.menus.Option(
                        display=lambda ctx: f"Mute log channel ({ctx.get_mentionable_channel(ctx).mention})",
                        component_display="Set mute log channel",
                        converters=[
                            vbu.menus.Converter(
                                prompt="What would you like to set the mute log channel to?",
                                converter=discord.TextChannel,
                            ),
                        ],
                        callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "mute_modlog_channel_id"),
                        cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "guild_settings", "mute_modlog_channel_id"),
                        allow_none=True,
                    ),
                    vbu.menus.Option(
                        display=lambda ctx: f"Warn log channel ({ctx.get_mentionable_channel(ctx).mention})",
                        component_display="Set warn log channel",
                        converters=[
                            vbu.menus.Converter(
                                prompt="What would you like to set the warn log channel to?",
                                converter=discord.TextChannel,
                            ),
                        ],
                        callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "warn_modlog_channel_id"),
                        cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "guild_settings", "warn_modlog_channel_id"),
                        allow_none=True,
                    ),
                    vbu.menus.Option(
                        display=lambda ctx: f"Edited message log channel ({ctx.get_mentionable_channel(ctx).mention})",
                        component_display="Set edited message log channel",
                        converters=[
                            vbu.menus.Converter(
                                prompt="What would you like to set the edited message log channel to?",
                                converter=discord.TextChannel,
                            ),
                        ],
                        callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "edited_message_modlog_channel_id"),
                        cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "guild_settings", "edited_message_modlog_channel_id"),
                        allow_none=True,
                    ),
                    vbu.menus.Option(
                        display=lambda ctx: f"Deleted message log channel ({ctx.get_mentionable_channel(ctx).mention})",
                        component_display="Set deleted message log channel",
                        converters=[
                            vbu.menus.Converter(
                                prompt="What would you like to set the deleted message log channel to?",
                                converter=discord.TextChannel,
                            ),
                        ],
                        callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "deleted_message_modlog_channel_id"),
                        cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "guild_settings", "deleted_message_modlog_channel_id"),
                        allow_none=True,
                    ),
                    vbu.menus.Option(
                        display=lambda ctx: f"VC update log channel ({ctx.get_mentionable_channel(ctx).mention})",
                        component_display="Set VC update log channel",
                        converters=[
                            vbu.menus.Converter(
                                prompt="What would you like to set the VC update log channel to?",
                                converter=discord.TextChannel,
                            ),
                        ],
                        callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "voice_update_modlog_channel_id"),
                        cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "guild_settings", "voice_update_modlog_channel_id"),
                        allow_none=True,
                    ),
                ),
            ),
        ),
    ),
    vbu.menus.Option(
        display="Fursona settings",
        callback=vbu.menus.Menu(
            vbu.menus.Option(
                display=lambda ctx: f"NSFW fursonas allowed (currently {ctx.bot.guild_settings[ctx.guild.id]['nsfw_is_allowed']})",
                component_display="Allow NSFW fursonas",
                converters=[
                    vbu.menus.Converter(
                        prompt="Should NSFW fursonas be allowed on your server?",
                        components=vbu.MessageComponents.boolean_buttons(),
                        converter=lambda payload: payload.component.custom_id == "YES",
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "nsfw_is_allowed"),
                cache_callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "nsfw_is_allowed"),
            ),
            vbu.menus.Option(
                display=lambda ctx: f"Fursona modmail channel (currently {ctx.get_mentionable_channel(ctx.bot.guild_settings[ctx.guild.id]['fursona_modmail_channel_id'])})",
                component_display="Set fursona modmail channel",
                converters=[
                    vbu.menus.Converter(
                        prompt="Where do you want to set your fursona modmail channel to?",
                        converter=discord.TextChannel,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_modmail_channel_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_modmail_channel_id"),
                allow_none=True,
            ),
            vbu.menus.Option(
                display=lambda ctx: f"Fursona decline archive channel (currently {ctx.get_mentionable_channel(ctx.bot.guild_settings[ctx.guild.id]['fursona_decline_archive_channel_id'])})",
                component_display="Set fursona decline archive",
                converters=[
                    vbu.menus.Converter(
                        prompt="Where should declined fursonas be archived to?",
                        converter=discord.TextChannel,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_decline_archive_channel_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_decline_archive_channel_id"),
                allow_none=True,
            ),
            vbu.menus.Option(
                display=lambda ctx: f"Fursona accept archive channel (currently {ctx.get_mentionable_channel(ctx.bot.guild_settings[ctx.guild.id]['fursona_accept_archive_channel_id'])})",
                component_display="Set fursona accept archive",
                converters=[
                    vbu.menus.Converter(
                        prompt="Where should accepted fursonas be archived to?",
                        converter=discord.TextChannel,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_accept_archive_channel_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_accept_archive_channel_id"),
                allow_none=True,
            ),
            vbu.menus.Option(
                display=lambda ctx: f"Fursona accept archive channel (currently {ctx.get_mentionable_channel(ctx.bot.guild_settings[ctx.guild.id]['fursona_accept_archive_channel_id'])})",
                component_display="Set fursona accept archive",
                converters=[
                    vbu.menus.Converter(
                        prompt="Where should accepted fursonas be archived to?",
                        converter=discord.TextChannel,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_accept_archive_channel_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_accept_archive_channel_id"),
                allow_none=True,
            ),
            vbu.menus.Option(
                display=lambda ctx: f"NSFW fursona accept archive channel (currently {ctx.get_mentionable_channel(ctx.bot.guild_settings[ctx.guild.id]['fursona_accept_nsfw_archive_channel_id'])})",
                component_display="Set NSFW fursona accept archive",
                converters=[
                    vbu.menus.Converter(
                        prompt="Where should NSFW accepted fursonas be archived to?",
                        converter=discord.TextChannel,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_accept_nsfw_archive_channel_id"),
                cache_callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "fursona_accept_nsfw_archive_channel_id"),
                allow_none=True,
            ),
            vbu.menus.Option(
                display="Sona counts by role",
                component_display="Set sona counts by role",
                callback=vbu.menus.MenuIterable(
                    select_sql="""SELECT * FROM role_list WHERE guild_id=$1 AND key='SonaCount'""",
                    select_sql_args=lambda ctx: (ctx.guild.id,),
                    insert_sql="""INSERT INTO role_list (guild_id, role_id, value, key) VALUES ($1, $2, $3, 'SonaCount')""",
                    insert_sql_args=lambda ctx, data: (ctx.guild.id, data[0].id, str(data[1])),
                    delete_sql="""DELETE FROM role_list WHERE guild_id=$1 AND role_id=$2 AND key='SonaCount'""",
                    delete_sql_args=lambda ctx, row: (ctx.guild.id, row['role_id'],),
                    converters=[
                        vbu.menus.Converter(
                            prompt="What role do you want to set the max sonas for?",
                            converter=discord.Role,
                        ),
                        vbu.menus.Converter(
                            prompt="How many sonas should people with this role be able to get?",
                            converter=int,
                        ),
                    ],
                    row_text_display=lambda ctx, row: f"{ctx.get_mentionable_role(row['role_id']).mention} - {int(row['value']):,}",
                    row_component_display=lambda ctx, row: ctx.get_mentionable_role(row['role_id']).name,
                    cache_callback=vbu.menus.Menu.callbacks.set_iterable_dict_cache(vbu.menus.DataLocation.GUILD, "role_sona_count"),
                    cache_delete_callback=vbu.menus.Menu.callbacks.delete_iterable_dict_cache(vbu.menus.DataLocation.GUILD, "role_sona_count"),
                    cache_delete_args=lambda row: (row['role_id'],)
                ),
            ),
        ),
    ),
    vbu.menus.Option(
        display="Interaction cooldowns per role",
        component_display="Set interaction cooldowns per role",
        callback=vbu.menus.MenuIterable(
            select_sql="""SELECT * FROM role_list WHERE guild_id=$1 AND key='Interactions'""",
            select_sql_args=lambda ctx: (ctx.guild.id,),
            insert_sql="""INSERT INTO role_list (guild_id, role_id, value, key) VALUES ($1, $2, $3, 'Interactions')""",
            insert_sql_args=lambda ctx, data: (ctx.guild.id, data[0].id, str(data[1].total_seconds())),
            delete_sql="""DELETE FROM role_list WHERE guild_id=$1 AND role_id=$2 AND key='Interactions'""",
            delete_sql_args=lambda ctx, row: (ctx.guild.id, row['role_id'],),
            converters=[
                vbu.menus.Converter(
                    prompt="What role do you want to set the interaction timeout for?",
                    converter=discord.Role,
                ),
                vbu.menus.Converter(
                    prompt="How long should this role's cooldown be (eg `5m`, `15s`, etc)?",
                    converter=vbu.TimeValue,
                ),
            ],
            row_text_display=lambda ctx, row: f"{ctx.get_mentionable_role(row['role_id']).mention} - {vbu.TimeValue(int(row['value'])).clean}",
            row_component_display=lambda ctx, row: ctx.get_mentionable_role(row['role_id']).name,
            cache_callback=vbu.menus.Menu.callbacks.set_iterable_dict_cache(vbu.menus.DataLocation.GUILD, "role_interaction_cooldowns"),
            cache_delete_callback=vbu.menus.Menu.callbacks.delete_iterable_dict_cache(vbu.menus.DataLocation.GUILD, "role_interaction_cooldowns"),
            cache_delete_args=lambda row: (row['role_id'],)
        ),
    ),
    vbu.menus.Option(
        display="Shop settings",
        callback=vbu.menus.Menu(
            vbu.menus.Option(
                display=lambda ctx: f"Paintbrush price (currently `{ctx.guild_settings[ctx.guild.id]['paintbrush_price']}`)",
                component_display="Set paintbrush price",
                converters=[
                    vbu.menus.Converter(
                        prompt="How much do you want a paintbrush to cost?",
                        checks=[
                            vbu.menus.Check(
                                check=lambda message: message.content and message.content.isdigit(),
                            ),
                        ],
                        converter=int,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "paintbrush_price"),
                cache_callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "paintbrush_price"),
                allow_none=True,
            ),
            vbu.menus.Option(
                display=lambda ctx: f"Cooldown token price (currently `{ctx.guild_settings[ctx.guild.id]['cooldown_token_price']}`)",
                component_display="Set cooldown token price",
                converters=[
                    vbu.menus.Converter(
                        prompt="How much do you want a cooldown token to cost?",
                        checks=[
                            vbu.menus.Check(
                                check=lambda message: message.content and message.content.isdigit(),
                            ),
                        ],
                        converter=int,
                    ),
                ],
                callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "cooldown_token_price"),
                cache_callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "cooldown_token_price"),
                allow_none=True,
            ),
            # vbu.menus.Option()  # Buyable roles
            # vbu.menus.Option()  # Temporary buyable roles
            # self.bot.dispatch("shop_message_update", ctx.guild)
        ),
    ),
    # vbu.menus.Option(
    #     display="Command disabling",
    #     callback=vbu.menus.Menu(
    #     ),
    # ),
)


# @setup.command()
# @vbu.checks.meta_command()
# async def botcommands(self, ctx: vbu.Context):
#     """
#     Bot command blacklisting setup.
#     """

#     menu = vbu.SettingsMenu()
#     menu.add_multiple_options(
#         vbu.SettingsMenuOption(
#             ctx=ctx,
#             display='Disable sona commands for channels',
#             callback=self.bot.get_command('setup disablesona')
#         ),
#         vbu.SettingsMenuOption(
#             ctx=ctx,
#             display='Disable interaction commands for channels',
#             callback=self.bot.get_command('setup disableinteractions')
#         ),
#     )
#     await menu.start(ctx)

# @setup.command()
# @vbu.checks.meta_command()
# async def disablesona(self, ctx: vbu.Context):
#     """
#     Sona channel disable setup.
#     """

#     menu = vbu.SettingsMenuIterable(
#         table_name="channel_list",
#         column_name="channel_id",
#         cache_key="disabled_sona_channels",
#         database_key="DisabledSonaChannel",
#         key_display_function=lambda k: getattr(ctx.guild.get_channel(k), 'mention', 'none'),
#         converters=[
#             vbu.SettingsMenuConverter(
#                 prompt="What channel you want the sona command to be disabled in?",
#                 asking_for="channel",
#                 converter=commands.TextChannelConverter,
#             ),
#         ]
#     )
#     await menu.start(ctx, clear_reactions_on_loop=True)

# @setup.command()
# @vbu.checks.meta_command()
# async def disableinteractions(self, ctx: vbu.Context):
#     """
#     Interaction channel disable setup.
#     """

#     menu = vbu.SettingsMenuIterable(
#         table_name="channel_list",
#         column_name="channel_id",
#         cache_key="disabled_interaction_channels",
#         database_key="DisabledInteractionChannel",
#         key_display_function=lambda k: getattr(ctx.guild.get_channel(k), 'mention', 'none'),
#         converters=[
#             vbu.SettingsMenuConverter(
#                 prompt="What channel you want the interaction commands to be disabled in?",
#                 asking_for="channel",
#                 converter=commands.TextChannelConverter,
#             ),
#         ]
#     )
#     await menu.start(ctx, clear_reactions_on_loop=True)


# @commands.group()
# @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True)
# @vbu.cooldown.cooldown(1, 60, commands.BucketType.member)
# @commands.guild_only()
# async def usersettings(self, ctx: vbu.Context):
#     """
#     User settings.
#     """

#     # Make sure it's only run as its own command, not a parent
#     if ctx.invoked_subcommand is not None:
#         return

#     # Create settings menu
#     menu = vbu.SettingsMenu()
#     settings_mention = vbu.SettingsMenuOption.get_user_settings_mention
#     menu.add_multiple_options(
#         vbu.SettingsMenuOption(
#             ctx=ctx,
#             display=lambda c: "Receive DM on paint removal (currently {0})".format(settings_mention(c, 'dm_on_paint_remove')),
#             converter_args=[
#                 vbu.SettingsMenuConverter(
#                     prompt="Do you want to receive a DM when paint is removed from you?",
#                     asking_for="paint DM",
#                     converter=vbu.converters.BooleanConverter,
#                     emojis=[self.TICK_EMOJI, self.CROSS_EMOJI],
#                 ),
#             ],
#             callback=vbu.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'dm_on_paint_remove'),
#         ),
#         vbu.SettingsMenuOption(
#             ctx=ctx,
#             display=lambda c: "Allow paint from other users (currently {0})".format(settings_mention(c, 'allow_paint')),
#             converter_args=[
#                 vbu.SettingsMenuConverter(
#                     prompt="Do you want to allow other users to paint you?",
#                     asking_for="paint enable",
#                     converter=vbu.converters.BooleanConverter,
#                     emojis=[self.TICK_EMOJI, self.CROSS_EMOJI],
#                 ),
#             ],
#             callback=vbu.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'allow_paint'),
#         ),
#         vbu.SettingsMenuOption(
#             ctx=ctx,
#             display=lambda c: "Allow interaction pings (currently {0})".format(settings_mention(c, 'receive_interaction_ping')),
#             converter_args=[
#                 vbu.SettingsMenuConverter(
#                     prompt="Do you want to be pinged when users run interactions on you?",
#                     asking_for="interaction ping",
#                     converter=vbu.converters.BooleanConverter,
#                     emojis=[self.TICK_EMOJI, self.CROSS_EMOJI],
#                 ),
#             ],
#             callback=vbu.SettingsMenuOption.get_set_user_settings_callback('user_settings', 'receive_interaction_ping'),
#         ),
#     )
#     try:
#         await menu.start(ctx)
#         await ctx.send("Done setting up!")
#     except vbu.errors.InvokedMetaCommand:
#         pass


# @setup.command()
# @vbu.checks.meta_command()
# async def buyableroles(self, ctx: vbu.Context):
#     """
#     Buyable roles setup.
#     """

#     menu = vbu.SettingsMenuIterable(
#         table_name="role_list",
#         column_name="role_id",
#         cache_key="buyable_roles",
#         database_key="BuyableRoles",
#         key_display_function=lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none'),
#         converters=[
#             vbu.SettingsMenuConverter(
#                 prompt="What role would you like to add to the shop?",
#                 asking_for="role",
#                 converter=commands.RoleConverter,
#             ),
#             vbu.SettingsMenuConverter(
#                 prompt="How much should the role cost?",
#                 asking_for="role price",
#                 converter=int,
#             ),
#         ]
#     )
#     await menu.start(ctx, clear_reactions_on_loop=True)

# @setup.command()
# @vbu.checks.meta_command()
# async def buyabletemproles(self, ctx: vbu.Context):
#     """
#     Buyable roles setup.
#     """

#     def add_callback(menu: vbu.SettingsMenu, ctx: vbu.Context):
#         async def callback(menu: vbu.SettingsMenu, role: discord.Role, price: int, duration: vbu.TimeValue):
#             async with ctx.bot.database() as db:
#                 await db(
#                     """INSERT INTO buyable_temporary_roles (guild_id, role_id, price, duration) VALUES ($1, $2, $3, $4)
#                     ON CONFLICT (guild_id, role_id) DO UPDATE SET price=excluded.price, duration=excluded.duration""",
#                     role.guild.id, role.id, price, duration.duration
#                 )
#             ctx.bot.guild_settings[ctx.guild.id]['buyable_temporary_roles'][role.id] = {'price': price, 'duration': duration.duration}
#         return callback

#     def delete_callback(menu: vbu.SettingsMenu, ctx: vbu.Context, role_id: int):
#         async def callback(menu: vbu.SettingsMenu):
#             async with ctx.bot.database() as db:
#                 await db(
#                     """DELETE FROM buyable_temporary_roles WHERE guild_id=$1 AND role_id=$2""",
#                     ctx.guild.id, role_id
#                 )
#             ctx.bot.guild_settings[ctx.guild.id]['buyable_temporary_roles'].pop(role_id)
#         return callback

#     menu = vbu.SettingsMenuIterable(
#         table_name="buyable_temporary_roles",
#         column_name="role_id",
#         cache_key="buyable_temporary_roles",
#         database_key="BuyableRoles",
#         key_display_function=lambda k: getattr(ctx.guild.get_role(k), 'mention', 'none'),
#         value_display_function=lambda v: f"{v['price']} for {vbu.TimeValue(v['duration']).clean}",
#         converters=[
#             vbu.SettingsMenuConverter(
#                 prompt="What role would you like to add to the shop?",
#                 asking_for="role",
#                 converter=commands.RoleConverter,
#             ),
#             vbu.SettingsMenuConverter(
#                 prompt="How much should the role cost?",
#                 asking_for="role price",
#                 converter=int,
#             ),
#             vbu.SettingsMenuConverter(
#                 prompt="How long should this role's cooldown be (eg `5m`, `15s`, etc)?",
#                 asking_for="role duration",
#                 converter=vbu.TimeValue,
#             ),
#         ],
#         iterable_add_callback=add_callback,
#         iterable_delete_callback=delete_callback,
#     )

#     await menu.start(ctx, clear_reactions_on_loop=True)
#     self.bot.dispatch("shop_message_update", ctx.guild)


def post_invoke(ctx):
    ctx.bot.dispatch("shop_message_update", ctx.guild)


def setup(bot: vbu.Bot):
    x = settings_menu.create_cog(
        bot,
        cog_name="BotSettings",
        post_invoke=post_invoke,
    )
    bot.add_cog(x)


def teardown(bot: vbu.Bot):
    bot.remove_cog("BotSettings")

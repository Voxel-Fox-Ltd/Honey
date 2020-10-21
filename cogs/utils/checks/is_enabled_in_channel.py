from discord.ext import commands


class DisabledInChannel(commands.CommandError):
    """The given command is disabled in the channel where it's being run"""
    pass


def is_enabled_in_channel(guild_settings_key:str):
    """Checks whether a command is disabled in a given channel or not

    Params:
        guild_settings_key : str
            The name of the key referring to the list of blacklisted channel IDs in the guild settings
    """

    async def predicate(ctx:commands.Context):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        guild_settings = ctx.bot.guild_settings[ctx.guild.id]
        channel_blacklist = guild_settings.setdefault(guild_settings_key, list())
        if ctx.channel.id in channel_blacklist:
            raise DisabledInChannel("You can't run that command in this channel.")
        return True
    return commands.check(predicate)

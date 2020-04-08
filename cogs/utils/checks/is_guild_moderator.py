import discord
from discord.ext import commands


class NotGuildModerator(commands.CommandError):
    """Thrown when the user doesn't have the guild moderator role."""

    def __init__(self, guild_moderator_role:discord.Role):
        self.guild_moderator_role = guild_moderator_role


def is_guild_moderator_predicate(ctx:commands.Context) -> bool:
    """Returns True if the the user has manage_messages perm or has a guild moderator role"""

    if ctx.author.guild_permissions.manage_messages:
        return True
    if ctx.bot.guild_settings[ctx.guild.id].get("guild_moderator_role_id", None) is None:
        return False
    if ctx.bot.guild_settings[ctx.guild.id].get("guild_moderator_role_id", None) in ctx.author._roles:
        return True
    return False


def is_guild_moderator():
    """Checks whether the user has manage_messages perm in the guild or has a guild moderator role"""

    async def predicate(ctx:commands.Context):

        if is_guild_moderator_predicate(ctx):
            return True
        mod_role_id = ctx.bot.guild_settings[ctx.guild.id].get("guild_moderator_role_id")
        mod_role = ctx.guild.get_role(mod_role_id)
        if mod_role is not None:
            raise NotGuildModerator(mod_role)
        raise commands.MissingPermissions(["manage_messages"])

    return commands.check(predicate)
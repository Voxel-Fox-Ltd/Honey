import discord
from discord.ext import commands


class NotGuildModerator(commands.MissingRole):
    """Thrown when the user doesn't have the guild moderator role."""


def is_guild_moderator_predicate(bot:commands.Bot, user:discord.Member) -> bool:
    """Returns True if the the user has manage_messages perm or has a guild moderator role"""

    guild_moderator_role_id = bot.guild_settings[user.guild.id].get("guild_moderator_role_id", None)
    if guild_moderator_role_id is None:
        return user.guild_permissions.manage_messages
    return guild_moderator_role_id in user._roles


def is_guild_moderator():
    """Checks whether the user has manage_messages perm in the guild or has a guild moderator role"""

    async def predicate(ctx:commands.Context):

        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        if is_guild_moderator_predicate(ctx.bot, ctx.author):
            return True
        mod_role_id = ctx.bot.guild_settings[ctx.guild.id].get("guild_moderator_role_id")
        mod_role = ctx.guild.get_role(mod_role_id)
        if mod_role is not None:
            raise NotGuildModerator(mod_role)
        raise commands.MissingPermissions(["manage_messages"])

    return commands.check(predicate)

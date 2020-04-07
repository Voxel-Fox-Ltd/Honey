import discord
from discord.ext import commands


class NotGuildModerator(commands.CommandError):
    """Thrown when the user doesn't have `manage_message` permission or the guild moderator role."""

    def __init__(self, guild_moderator_role):
        self.guild_moderator_role = guild_moderator_role or None
        self.default_permission = "manage_message"
        message = 'You need the `{0}` permission or the guild moderator role ({1.name})!'.format(default_permission, guild_moderator_role)
        super().__init__(message)


def is_guild_moderator_predicate(ctx:commands.Context):
    """Returns True if the the user has manage_message perm or has a guild moderator role"""

    def has_perms(**perms):
        def predicate(ctx):
            ch = ctx.channel
            permissions = ch.permissions_for(ctx.author)

            missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

            if not missing:
                return True

            return missing

    if has_perms(manage_messages=True):
        return True
    
    if ctx.bot.guild_settings[ctx.guild.id]["guild_moderator_role_id"] == None:
        return False

    if ctx.bot.guild_settings[ctx.guild.id]["guild_moderator_role_id"] in ctx.author._roles:
        return True


def is_guild_moderator():
    """Checks whether the user has manage_message perm or has a guild moderator role"""

    async def predicate(ctx:commands.Context):

        if is_guild_moderator_predicate(ctx):
            return True
        mod_role_id = ctx.bot.guild_settings[ctx.guild.id].get("guild_moderator_role_id")
        if mod_role_id is None:
            return None
        raise NotGuildModerator(ctx.guild.get_role(mod_role_id))

    return commands.check(predicate)
import discord
from discord.ext import commands


class NotGuildModerator(commands.CommandError):
    """Thrown when the user doesn't have `manage_message` permission or the guild moderator role."""

    def __init__(self, guild_moderator_role):
        self.guild_moderator_role = guild_moderator_role or None
        self.default_permission = "manage_message"
        if self.guild_moderator_role == None:
            message = 'You need the `{0}` permission or the guild moderator role ({1})!'.format(self.default_permission, self.guild_moderator_role)
        else:
            message = 'You need the `{0}` permission or the guild moderator role (`None`)!'.format(self.default_permission)
        super().__init__(message)


def is_guild_moderator_predicate(ctx:commands.Context):
    """Returns True if the the user has manage_message perm or has a guild moderator role"""

    if ctx.author.guild_permissions.manage_messages:
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
        if mod_role_id is not None:
            raise NotGuildModerator(ctx.guild.get_role(mod_role_id))
        raise NotGuildModerator(None)

    return commands.check(predicate)
from discord.ext import commands


class IsNotVerified(commands.MissingRole):
    """The user is missing the verified role"""

    def __init__(self):
        super().__init__("Verified")


def is_verified(ctx):
    """Returns whether or not the user has the verified role
    in the guild or not; raises IsNotVerified"""

    guild_config = ctx.bot.guild_settings[ctx.guild.id]
    verified_role = guild_config.get("verified_role")
    if verified_role is None:
        return True
    if verified_role in ctx.author._roles:
        return True
    raise IsNotVerified()

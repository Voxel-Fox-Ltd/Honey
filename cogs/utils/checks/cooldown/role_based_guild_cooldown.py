import sys

from discord.ext import commands

from cogs.utils.checks.cooldown.cooldown import Cooldown, GroupedCooldownMapping


class RoleBasedGuildCooldown(Cooldown):

    # tier_cooldowns  # GuildID: {Optional[RoleID]: Seconds}

    _copy_kwargs = ("original_per")

    def __init__(self, key:str, *args, **kwargs):
        super().__init__(mapping=GroupedCooldownMapping(key=key), *args, **kwargs)

    def predicate(self, ctx:commands.Context):
        """Update the cooldown based on the given guild member"""

        # Get the guild settings
        guild_settings = ctx.bot.guild_settings[ctx.guild.id]
        cooldown_settings = guild_settings.get("role_interaction_cooldowns")

        # Find the lowest number on the guild
        rate_per = min(cooldown_settings.get(i, sys.maxsize) for i in ctx.author._roles)

        # It's the max int size? Let's just set that back to original
        if rate_per == sys.maxsize:
            rate_per = self.original_per

        # And update
        self.per = rate_per

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        self.original_per = self.per

import sys

from discord.ext import commands

from cogs.utils.checks.cooldown.cooldown import Cooldown


class RoleBasedGuildCooldown(Cooldown):

    # tier_cooldowns  # GuildID: {Optional[RoleID]: Seconds}

    def predicate(self, ctx:commands.Context):
        """Update the cooldown based on the given guild member"""

        # Get the guild settings
        cooldown_settings = ctx.bot.guild_settings[ctx.guild.id]['role_interaction_cooldowns']

        # Find the lowest number on the guild
        rate_per = min(int(cooldown_settings.get(i, sys.maxsize)) for i in ctx.author._roles)

        # If it's maxsize now they don't have any cooldown info set
        if rate_per == sys.maxsize:
            rate_per = self.original_per

        # And update
        self.per = rate_per

    def __call__(self, *args, **kwargs):
        v = super().__call__(*args, **kwargs)
        self.original_per = self.per
        return v

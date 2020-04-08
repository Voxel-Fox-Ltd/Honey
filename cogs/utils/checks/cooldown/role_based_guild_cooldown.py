import sys

from discord.ext import commands

from cogs.utils.checks.cooldown.cooldown import Cooldown


class RoleBasedGuildCooldown(Cooldown):

    # tier_cooldowns  # GuildID: {Optional[RoleID]: Seconds}

    def predicate(self, ctx:commands.Context):
        """Update the cooldown based on the given guild member"""

        # Get the guild settings
        guild_settings = ctx.bot.guild_settings[ctx.guild.id]
        cooldown_settings = guild_settings.get("role_interaction_cooldowns", {})

        # Find the lowest number on the guild
        rate_per = min(cooldown_settings.get(i, sys.maxsize) for i in ctx.author._roles)

        # If it's maxsize now they don't have any cooldown-applicable roles
        try:
            rate_per = max(cooldown_settings.values())  # Set it to the max value in their settings
        except ValueError:
            pass

        # If it's maxsize now they don't have any cooldown info set
        if rate_per == sys.maxsize:
            rate_per = self.original_per

        # And update
        self.per = rate_per

    def __call__(self, *args, **kwargs):
        v = super().__call__(*args, **kwargs)
        self.original_per = self.per
        return v

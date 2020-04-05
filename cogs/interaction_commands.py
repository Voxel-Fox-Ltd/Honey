import random

from discord.ext import commands

from cogs import utils


cooldown = utils.cooldown.RoleBasedGuildCooldown(key="interactions")


interaction_responses = {
    "hug": [
        "*{author} snuggles up to {user}, hugging them tightly.*",
        "*{author} gives {user} a tight huggo.*",
        "*{author} sneaks up to {user}, tacklehugging them from behind.*",
        "*{author} lunges at {user}, wrapping their arms aroung them tightly.*"
    ],
}


def command_has_responses(ctx):
    if len(interaction_responses.get(ctx.command.name, list())) > 0:
        return True
    raise commands.DisabledCommand()


class InteractionCommands(utils.Cog):

    @commands.command(cls=utils.Command, cooldown_after_parsing=True)
    @utils.cooldown.cooldown(1, 60 * 10, commands.BucketType.member, cls=cooldown)
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def hug(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to hug a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name).format(author=ctx.author.mention, user=user.mention)
        ))


def setup(bot:utils.Bot):
    x = InteractionCommands(bot)
    bot.add_cog(x)

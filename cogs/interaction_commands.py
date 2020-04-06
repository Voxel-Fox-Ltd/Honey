import random

from discord.ext import commands

from cogs import utils


interaction_responses = {
    "hug": [
        "*{author} snuggles up to {user}, hugging them tightly.*",
        "*{author} gives {user} a tight huggo.*",
        "*{author} sneaks up to {user}, tacklehugging them from behind.*",
        "*{author} lunges at {user}, wrapping their arms aroung them tightly.*"
    ],
    "pat": [
        "*{author} leans forward, now looking down on {user} and softly pats their head.*",
        "*{author} decided today was a good day for pats. {user}, you're up!*",
        "*{author} jumps around until they find themselves patting {user}. Cute!*",
        "*It looks like {user} was begging for pats! So {author} gave them one.*",
    ],
    "lick": [
        "*{author} zooms over to {user} and gives them a lick.*",
        "*{user} was caught being a big bad! {author} decides to lick them as punishment!*",
        "*{author} playfully licks {user}.*",
        "*Whilst {user} was trying to blep and be cute. {author} decided to ruin the mood and lick them.*",
    ],
    "kiss": [
        "*{user} felt embarrassed after being kissed by {author}!*",
        "*{author} felt like the time was right, and kissed {user}.*",
        "*Time stopped for {user} as they began to blush a bright red when they realised {author} was kissing them!*",
        "*It looked like everything was going wrong until {author} kissed {user}.*",
    ],
    "bap": [
        "*{author} decided that {user} was misbehaving and bapped them!*",
        "*{user} was running away until {author} caught up with them, and hit them on their snoot!*",
        "*{author} was carefully following {user} until -- {author} leapt out to attack {user} and bapped them.*",
        "*{author} had had enough! {user} passed out after {author} bapped them!*",
    ],
    "boop": [
        "*{author} runs at {user} and lightly taps them on their nose! Boop!*",
        "*{user} was pointing to their snoot and {author} decided to boop it.*",
        "*{author} was admiring the look of {user}'s snoot, so much so they decided boop it.*",
        "*{user} felt the paw of {author} touching their nose. Embarrassed after realising they got booped.*",
    ],
}


def command_has_responses(ctx):
    if len(interaction_responses.get(ctx.command.name, list())) > 0:
        return True
    raise commands.DisabledCommand()


class InteractionCommands(utils.Cog):

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=['cuddle', 'snuggle', 'snug'])
    @utils.cooldown.cooldown(1, 60 * 10, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def hug(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to hug a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=['pet'])
    @utils.cooldown.cooldown(1, 60 * 10, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def pat(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to pat a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 10, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def lick(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to lick a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=['smooch'])
    @utils.cooldown.cooldown(1, 60 * 10, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def kiss(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to kiss a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 10, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def bap(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to bap a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 10, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def boop(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to boop a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))


def setup(bot:utils.Bot):
    x = InteractionCommands(bot)
    bot.add_cog(x)

import random

from discord.ext import commands

from cogs import utils


interaction_responses = {
    "hug": [
        "*{author} snuggles up to {user}, hugging them tightly.*",
        "*{author} gives {user} a tight huggo.*",
        "*{author} sneaks up to {user}, tacklehugging them from behind.*",
        "*{author} lunges at {user}, wrapping their arms around them tightly.*",
        "*{author} was excited to see {user} and hugged them tightly with a smile.*",
        "*{user} walked out of a store when they unexpectedly received a hug from {author}.*",
        "*{user} asked for a hug from {author} and got what they wanted.*",
        "*{author} sneakily walked up behind {user} and gave them a fluffy hug*",
        "*As {user} talked, {author} went up to them and hugged them.*",
        "*{author} ran up to a friend, {user}, and gave them a firm hug.*",
        "*{user} wasn't suspecting anything at first, but then suddenly {author} appears and hugs them!*",
        "*{user} felt depressed until {author} came up and gave them a friendly hug.*",
        "*{author} embraces {user} with a really warm loving cuddle.*",
        "*{author} grabbed {user} from behind and pulled them into a cuddle with their arms wrapped around tightly.*",
        "*{author} pulled {user} close and held them in a warm cuddle. How sweet.*",
    ],
    "pat": [
        "*{author} leans forward, now looking down on {user} and softly pats their head.*",
        "*{author} decided today was a good day for pats. {user}, you're up!*",
        "*{author} jumps around until they find themselves patting {user}. Cute!*",
        "*It looks like {user} was begging for pats! So {author} gave them one.*",
        "*{author} gave {user} some pats to cheer them up.*",
        "*{author} looks over at {user}, who is rolling around and begging for pats.*",
        "*{user} happily nuzzles into {author}'s hand and bleps as {author} gives them lots of pats.*",
        "*{author} give {user} some pats to cheer them up.*",
        "*{author} graces {user}'s head with gentle pats.*",
        "*{user} makes nonstop animal noises until {author} gives them pats.*",
        "*{user} rolls over to {author} and gets some nice pats.*",
        "*{author} gives {user} official pats of approval!*",
        "*{user} flops onto {author}'s lap for gentle adorable pats.*",
        "*{user} rolls over to {author} and gets some nice pats.*",
        "*{user} happily nuzzles into {author}'s hand and bleps as {author} gives them lots of pats.*",
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
    "hold": [
        "*\"I'm never letting you go\", {author} says to {user} while holding them.*",
        "*{author} holds {user} with a deep passionate smile.*",
        "*{author} holds {user} tightly saying, \"I'm never letting go\".*",
    ],
    "nuzzle": [
        "*{author} lays down with {user}, nuzzling after a hard day.*",
        "*{author} and {user} relax together, nuzzling each other in a loving embrace.*",
        "*{author} nuzzles {user} as they watch a romantic movie.*",
        "*{author} nuzzles {user} affectionately to keep warm on a cold night. How adorable~!*",
        "*{author} nuzzles {user} in bed before they fell asleep.*",
        "*{author} sits down with {user}, nuzzling them in their lap.*",
        "*{author} nuzzles {user} with passionate love as they watch the sunset.*",
    ],
    "pounce": [
        "*{author} swoops down on {user} giving them a big surprise!*",
        "*{author} looks at {user} and pounce on them with a very smirky smile.*",
        "*{author} pounces {user} on their bed.*",
        "*{author} knocks over {user} with a powerful pounce, but to {author}'s surprise, {user} retaliates with a pounce of their own!*",
        "*Unexpectedly, {author} pounces on {user} making {author} fall flat into the snow!*",
        "*{author} pounces on {user}; \"tag, you're it!\"*",
        "*{author} locks onto {user} and does a well-aimed pounce onto the floor!*",
        "*{author} pounces on {user} in a happy playful mood.*",
    ],
    "dance": [
        "*{author} put on their favorite song and took {user}'s hand, pulling them in for a quick dance.*",
        "*With the music reaching their favorite part, {author} grabbed {user} and spun them into an exciting dance.*",
        "*{author} decided that sitting idly by wasn't going to cut it, so they pulled {user} in for a dance.*",
    ],
    "poke": [
        "*{author} sneaks up behind {user}, pokes them, and runs away giggling. What a cutie. *",
        "*Hey {user}, {author} wanted your attention! *",
        "*Pssst... {user}... poke poke*",
    ],
    "punch": [
        "*{author} threw their hardest, strongest right hook right at {user}'s nose.. that one's gonna hurt in the morning..*",
        "*Without a moments hesitation, {author} quickly landed a flawless jab into {user}'s eye.*",
        "*{user} danced with the devil for far too long and caught a swift uppercut from {author}.*",
    ],
    "slap": [
        "*{author} slipped on a fancy, white silk glove and elegantly slapped {user}'s face. That'll teach you to mess with them.*",
        "*{author} got sick and tired of hearing {user}, so they 'calmly' slapped the attitude right out of them.*",
        "*{author} lined up the perfect swing, to accurately and powerfully decimate {user}'s face with a hard slap.*",
    ],
    "tug": [
        "*{author} grabbed {user}'s tail and tugged gently. *",
        "*{author} snuck up behind {user}, grabbed their tail and tugged hard, giggling. *",
        "*{user} was minding their own business when {author} came over and tugged on their ear.*",
    ],
    "yeet": [
        "*{author} picks up {user}, yeeting them as far as the eye can see. They won't be coming back anytime soon. *",
        "*{user} was being annoying, so {author} picked them up and yeeted them 30 miles; what a throw!*",
    ],
}


def command_has_responses(ctx):
    if len(interaction_responses.get(ctx.command.name, list())) > 0:
        return True
    raise commands.DisabledCommand()


class InteractionCommands(utils.Cog):

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=['cuddle', 'snuggle', 'snug'])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def hug(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to hug a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=['pet'])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def pat(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to pat a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def lick(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to lick a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=['smooch'])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def kiss(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to kiss a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def bap(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to bap a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def boop(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to boop a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def hold(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to hold a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def nuzzle(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to nuzzle a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def pounce(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to pounce a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def dance(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Lets you dance with a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def poke(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Lets you poke a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def punch(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to punch a user >:c"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def slap(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to slap a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def tug(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Allows you to tug on a user"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))

    @commands.command(cls=utils.Command, cooldown_after_parsing=True, aliases=[])
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @commands.check(command_has_responses)
    @commands.bot_has_permissions(send_messages=True)
    async def yeet(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """Lets you fumkin YEET someone"""

        return await ctx.send(random.choice(
            interaction_responses.get(ctx.command.name)
        ).format(author=ctx.author.mention, user=user.mention))


def setup(bot:utils.Bot):
    x = InteractionCommands(bot)
    bot.add_cog(x)

import collections

import discord
from discord.ext import commands

from cogs import utils


COMMON_COMMAND_ALIASES = (
    ("hug", "cuddle", "snuggle", "snug",),
    ("pat", "pet",),
    ("kiss", "smooch",),
)


class InteractionCommands(utils.Cog):

    @utils.Cog.listener()
    async def on_interaction_run(self, ctx):
        """Saves an interaction value into the database"""

        if ctx.guild is None:
            return
        async with self.bot.database() as db:
            await db(
                """INSERT INTO interaction_counter (guild_id, user_id, target_id, interaction, amount)
                VALUES ($1, $2, $3, $4, 1) ON CONFLICT (guild_id, user_id, target_id, interaction) DO UPDATE SET
                amount=interaction_counter.amount+excluded.amount""", ctx.guild.id, ctx.author.id, ctx.args[-1].id, ctx.interaction_name
            )

    @commands.group(cls=utils.Group, aliases=['interaction'], invoke_without_command=True)
    @utils.checks.is_enabled_in_channel('disabled_interaction_channels')
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def interactions(self, ctx:utils.Context, user:discord.Member=None):
        """Shows you your interaction statistics"""

        if ctx.invoked_subcommand is not None:
            return

        # Get the interaction numbers
        user = user or ctx.author
        async with self.bot.database() as db:
            valid_interaction_rows = await db(
                "SELECT DISTINCT interaction_name FROM interaction_text WHERE guild_id=ANY($1::BIGINT[])",
                [0, ctx.guild.id]
            )
            given_rows = await db(
                "SELECT interaction, SUM(amount) AS amount FROM interaction_counter WHERE user_id=$1 AND guild_id=$2 GROUP BY guild_id, user_id, interaction",
                user.id, ctx.guild.id
            )
            received_rows = await db(
                "SELECT interaction, SUM(amount) AS amount FROM interaction_counter WHERE target_id=$1 AND guild_id=$2 GROUP BY guild_id, target_id, interaction",
                user.id, ctx.guild.id
            )
        valid_interactions = sorted([i['interaction_name'] for i in valid_interaction_rows])

        # Sort them into useful dicts
        given_interactions = collections.defaultdict(int)
        for row in given_rows:
            given_interactions[row['interaction']] = row['amount']
        received_interactions = collections.defaultdict(int)
        for row in received_rows:
            received_interactions[row['interaction']] = row['amount']

        # And now into an embed
        with utils.Embed(use_random_colour=True) as embed:
            embed.set_author_to_user(user=user)
            for i in valid_interactions:
                embed.add_field(i.title(), f"Given {given_interactions[i]} || Received {received_interactions[i]}")
        await ctx.send(embed=embed)

    @utils.Cog.listener()
    async def on_command_error(self, ctx:utils.Context, error:commands.CommandError):
        """Listens for command not found errors and tries to run them as interactions"""

        if not isinstance(error, commands.CommandNotFound):
            return

        # Deal with common aliases
        command_name = ctx.invoked_with.lower()
        for aliases in COMMON_COMMAND_ALIASES:
            if command_name in aliases:
                command_name = aliases[0]

        # See if we wanna deal with it
        guild_ids = [0] if ctx.guild is None else [0, ctx.guild.id]
        async with self.bot.database() as db:
            rows = await db(
                "SELECT response FROM interaction_text WHERE interaction_name=$1 AND guild_id=ANY($2::BIGINT[]) ORDER BY RANDOM() LIMIT 1",
                command_name.lower(), guild_ids
            )
        if not rows:
            self.logger.info("Nothing found")
            return  # No responses found

        # Create a command we can invoke
        ctx.interaction_response = rows[0]['response']
        ctx.interaction_name = command_name
        ctx.invoke_meta = True
        ctx.command = self.bot.get_command("interaction_command_meta")
        await self.bot.invoke(ctx)

    @commands.command(cls=utils.Command, cooldown_after_parsing=True)
    @utils.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=utils.cooldown.GroupedCooldownMapping("interactions")))
    @utils.checks.is_enabled_in_channel('disabled_interaction_channels')
    @commands.bot_has_permissions(send_messages=True)
    @utils.checks.meta_command()
    async def interaction_command_meta(self, ctx:utils.Context, user:utils.converters.NotAuthorMember):
        """The interaction command invoker"""

        await ctx.send(ctx.interaction_response.replace("{author}", ctx.author.mention).replace("{user}", user.mention))
        self.bot.dispatch("interaction_run", ctx)

    @interactions.command(cls=utils.Command)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def add(self, ctx:utils.Context, interaction_name:str, *, response:str):
        """Adds a custom interaction
        Use `{author}` and `{user}` as placeholders for where users should receive a ping
        All interactions must ping one user that isn't the author
        """

        if len(interaction_name) > 50:
            return await ctx.send("That interaction name is too long.")
        if not response:
            raise utils.errors.MissingRequiredArgumentString("response")
        async with self.bot.database() as db:
            await db(
                "INSERT INTO interaction_text (guild_id, interaction_name, response) VALUES ($1, $2, $3)",
                ctx.guild.id, interaction_name, f"*{response.strip('* ')}*"
            )
        return await ctx.send("Added your custom interaction response to the pool.")


def setup(bot:utils.Bot):
    x = InteractionCommands(bot)
    bot.add_cog(x)

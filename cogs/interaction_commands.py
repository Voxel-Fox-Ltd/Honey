import collections
import fractions

import discord
from discord.ext import commands
import voxelbotutils as vbu

from cogs import utils


COMMON_COMMAND_ALIASES = (
    ("hug", "cuddle", "snuggle", "snug",),
    ("pat", "pet", "headpat",),
    ("kiss", "smooch",),
)


class InteractionCommands(vbu.Cog):

    @vbu.Cog.listener()
    async def on_interaction_run(self, ctx):
        """
        Saves an interaction value into the database.
        """

        if ctx.guild is None:
            return
        async with self.bot.database() as db:
            await db(
                """INSERT INTO interaction_counter (guild_id, user_id, target_id, interaction, amount)
                VALUES ($1, $2, $3, $4, 1) ON CONFLICT (guild_id, user_id, target_id, interaction) DO UPDATE SET
                amount=interaction_counter.amount+excluded.amount""", ctx.guild.id, ctx.author.id, ctx.args[-1].id, ctx.interaction_name
            )

    @vbu.group(aliases=['interaction'], invoke_without_command=True)
    @utils.checks.is_enabled_in_channel('disabled_interaction_channels')
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def interactions(self, ctx: vbu.Context, user: discord.Member = None):
        """
        Shows you your interaction statistics.
        """

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
        with vbu.Embed(use_random_colour=True) as embed:
            embed.set_author_to_user(user=user)
            for i in valid_interactions:
                given = given_interactions[i]
                received = received_interactions[i]
                if given > 0 and received > 0:
                    fraction = fractions.Fraction(given, received)
                    embed.add_field(i.title(), f"Given {given}, received {received} ({fraction.numerator:.0f}:{fraction.denominator:.0f})")
                else:
                    embed.add_field(i.title(), f"Given {given}, received {received}")
        await ctx.send(embed=embed)

    @vbu.Cog.listener()
    async def on_command_error(self, ctx: vbu.Context, error: commands.CommandError):
        """
        Listens for command not found errors and tries to run them as interactions.
        """

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

    @vbu.command(cooldown_after_parsing=True)
    @vbu.cooldown.cooldown(1, 60 * 30, commands.BucketType.member, cls=utils.cooldown.RoleBasedGuildCooldown(mapping=vbu.cooldown.GroupedCooldownMapping("interactions")))
    @utils.checks.is_enabled_in_channel('disabled_interaction_channels')
    @commands.bot_has_permissions(send_messages=True)
    @vbu.checks.meta_command()
    async def interaction_command_meta(self, ctx: vbu.Context, user: vbu.converters.FilteredUser(allow_author=False, allow_bots=True)):
        """
        The interaction command invoker.
        """

        # Set up who we're pinging
        pings = []
        ping_author = self.bot.user_settings[ctx.author.id]['receive_interaction_ping']
        if ping_author:
            pings.append(ctx.author)
        ping_user = self.bot.user_settings[user.id]['receive_interaction_ping']
        if ping_user:
            pings.append(user)
        await ctx.send(
            ctx.interaction_response.replace("{author}", ctx.author.mention).replace("{user}", user.mention),
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=pings)
        )
        self.bot.dispatch("interaction_run", ctx)

    @vbu.command(aliases=['cd'])
    @commands.bot_has_permissions(send_messages=True)
    async def cooldown(self, ctx: vbu.Context):
        """
        Tells you how long your remaining interaction cooldown is.
        """

        interaction = self.bot.get_command("interaction_command_meta")
        remaining_time = interaction.get_remaining_cooldown(ctx)
        if not remaining_time or remaining_time < 1:
            return await ctx.send("Your interaction cooldown has expired - you're able to run interactions again.")
        return await ctx.send(f"Your remaining cooldown is {vbu.TimeValue(remaining_time).clean}.")

    @interactions.command()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def add(self, ctx: vbu.Context, interaction_name: str, *, response: str):
        """
        Adds a custom interaction.
        Use `{author}` and `{user}` as placeholders for where users should receive a ping.
        All interactions must ping one user that isn't the author.
        """

        if len(interaction_name) > 50:
            return await ctx.send("That interaction name is too long.")
        if not response:
            raise vbu.errors.MissingRequiredArgumentString("response")
        async with self.bot.database() as db:
            await db(
                "INSERT INTO interaction_text (guild_id, interaction_name, response) VALUES ($1, $2, $3)",
                ctx.guild.id, interaction_name.lower(), f"*{response.strip('* ')}*"
            )
        return await ctx.send("Added your custom interaction response to the pool.")

    @interactions.command(aliases=['nsfwadd'])
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def addnsfw(self, ctx: vbu.Context, interaction_name: str, *, response: str):
        """
        Adds a custom NSFW interaction.
        Use `{author}` and `{user}` as placeholders for where users should receive a ping.
        All interactions must ping one user that isn't the author.
        """

        if len(interaction_name) > 50:
            return await ctx.send("That interaction name is too long.")
        if not response:
            raise vbu.errors.MissingRequiredArgumentString("response")
        async with self.bot.database() as db:
            await db(
                "INSERT INTO interaction_text (guild_id, interaction_name, response) VALUES ($1, $2, $3)",
                ctx.guild.id, interaction_name.lower(), f"*{response.strip('* ')}*"
            )
        return await ctx.send("Added your custom interaction response to the pool.")


def setup(bot: vbu.Bot):
    x = InteractionCommands(bot)
    bot.add_cog(x)

import discord

from cogs import utils


class EconomyHandler(utils.Cog):

    @utils.Cog.listener("on_ready")
    async def free_money_handler(self):
        """Listens for ready being pinged and then makes sure every member in every guild has
        10k given to the bot's account in their name"""

        async with self.bot.database() as db:

            # Let's go through E V E R Y O N E
            for guild in self.bot.guilds:
                for member in guild.members:

                    # Filter out bots
                    if member.bot:
                        continue

                    # See if they already got money
                    rows = await db("SELECT * FROM user_money WHERE guild_id=$1 AND user_id=$2", guild.id, member.id)
                    if rows:
                        continue

                    # Add some money to the bot user
                    await db.start_transaction()
                    await db(
                        """INSERT INTO user_money (guild_id, user_id, amount) VALUES
                        ($1, $2, 10000) ON CONFLICT (guild_id, user_id)
                        DO UPDATE SET amount=user_money.amount+excluded.amount""",
                        guild.id, guild.me.id
                    )
                    await db("INSERT INTO user_money (guild_id, user_id, amount) VALUES ($1, $2, 0)", guild.id, member.id)
                    await db.commit_transaction()

    @utils.Cog.listener("on_member_join")
    async def member_join_free_money_handler(self, member:discord.Member):
        """Pinged when a member joins the guild - add 10k to the bot in this case"""

        async with self.bot.database() as db:

            # Filter out bots
            if member.bot:
                return

            # See if they already got money
            rows = await db("SELECT * FROM user_money WHERE guild_id=$1 AND user_id=$2", member.guild.id, member.id)
            if rows:
                return

            # Add some money to the bot user
            await db.start_transaction()
            await db(
                """INSERT INTO user_money (guild_id, user_id, amount) VALUES
                ($1, $2, 10000) ON CONFLICT (guild_id, user_id)
                DO UPDATE SET amount=user_money.amount+excluded.amount""",
                member.guild.id, member.guild.me.id
            )
            await db("INSERT INTO user_money (guild_id, user_id, amount) VALUES ($1, $2, 10000)", member.guild.id, member.id)
            await db.commit_transaction()


def setup(bot:utils.Bot):
    x = EconomyHandler(bot)
    bot.add_cog(x)

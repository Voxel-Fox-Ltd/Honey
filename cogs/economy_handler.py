import collections
import random
import re
from datetime import datetime as dt, timedelta

import discord
from discord.ext import commands

from cogs import utils


class EconomyHandler(utils.Cog):

    EMOJI_REGEX = re.compile(r"<:.{1,32}:\d{16,32}>")

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.last_message = collections.defaultdict(lambda: dt(2000, 1, 1))

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
            await db("INSERT INTO user_money (guild_id, user_id, amount) VALUES ($1, $2, 0)", member.guild.id, member.id)
            await db.commit_transaction()

    @commands.command(cls=utils.Command, enabled=False)
    @utils.cooldown.cooldown(1, 60 * 60, commands.BucketType.member)
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def work(self, ctx:utils.Context):
        """Do some work to get you goin with some money wew"""

        # Make sure there's money set up
        if self.bot.guild_settings[ctx.guild.id].get('shop_message_id') is None:
            return await ctx.send("There's no shop set up for this server, so there's no point in you getting money. Sorry :/")

        # Add some money to the user
        amount = random.randint(25, 75)
        async with self.bot.database() as db:
            await db.start_transaction()
            await db(
                "UPDATE user_money SET amount=user_money.amount+$3 WHERE guild_id=$1 AND user_id=$2",
                ctx.guild.id, ctx.author.id, amount,
            )
            await db(
                "UPDATE user_money SET amount=user_money.amount-$3 WHERE guild_id=$1 AND user_id=$2",
                ctx.guild.id, ctx.guild.me.id, amount,
            )
            await db.commit_transaction()

        # Make us an output
        work_text = random.choice([
            "Placeholder work text giving you {amount} coins xoxo"
        ]).format(guild=ctx.guild, user=ctx.author, channel=ctx.channel, amount=amount)
        await ctx.send(work_text)

    @utils.Cog.listener("on_message")
    async def user_message_money_handler(self, message:discord.Message):
        """Add some money to the user's account when they send a message"""

        # Add some filters
        if message.guild is None:
            return
        clean_emojiless_content = self.EMOJI_REGEX.sub("x", message.clean_content)
        if len(clean_emojiless_content.replace(" ", "")) <= 3:
            return
        if message.author.bot:
            return
        if self.last_message[(message.guild.id, message.author.id)] + timedelta(minutes=1) > dt.utcnow():
            return

        # Update timestamp
        self.last_message[(message.guild.id, message.author.id)] = dt.utcnow()

        # Add some money to the user
        amount = random.randint(15, 25)
        async with self.bot.database() as db:
            await db.start_transaction()
            await db(
                "UPDATE user_money SET amount=user_money.amount+$3 WHERE guild_id=$1 AND user_id=$2",
                message.guild.id, message.author.id, amount,
            )
            await db(
                "UPDATE user_money SET amount=user_money.amount-$3 WHERE guild_id=$1 AND user_id=$2",
                message.guild.id, message.guild.me.id, amount,
            )
            await db.commit_transaction()


def setup(bot:utils.Bot):
    x = EconomyHandler(bot)
    bot.add_cog(x)

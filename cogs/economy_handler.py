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

                    # Add some money to the bot user
                    await db(
                        "INSERT INTO user_money (guild_id, user_id, amount) VALUES ($1, $2, 0) ON CONFLICT (guild_id, user_id) DO NOTHING",
                        guild.id, member.id
                    )

    @utils.Cog.listener("on_member_join")
    async def member_join_free_money_handler(self, member:discord.Member):
        """Pinged when a member joins the guild - add 10k to the bot in this case"""

        async with self.bot.database() as db:

            # Filter out bots
            if member.bot:
                return

            # Add some money to the bot user
            await db(
                "INSERT INTO user_money (guild_id, user_id, amount) VALUES ($1, $2, 0) ON CONFLICT (guild_id, user_id) DO NOTHING",
                member.guild.id, member.id
            )

    @utils.Cog.listener("on_guild_join")
    async def guild_join_free_money_handler(self, guild:discord.Guild):
        """Pinged when a member joins the guild - add 10k to the bot in this case"""

        async with self.bot.database() as db:
            for member in guild.members:

                # Filter out bots
                if member.bot:
                    continue

                # Add some money to the bot user
                await db(
                    "INSERT INTO user_money (guild_id, user_id, amount) VALUES ($1, $2, 0) ON CONFLICT (guild_id, user_id) DO NOTHING",
                    guild.id, member.id
                )

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

        # Make sure it's in a server
        if message.guild is None:
            return

        # Make sure there's a shopping channel set
        if self.bot.guild_settings[message.guild.id].get('shop_message_id') is None:
            return

        # Make sure they've actually said something
        clean_emojiless_content = self.EMOJI_REGEX.sub("x", message.clean_content)
        if len(clean_emojiless_content.replace(" ", "")) <= 3:
            return

        # Make sure they're not a bot
        if message.author.bot:
            return

        # Check time limit
        if self.last_message[(message.guild.id, message.author.id)] + timedelta(minutes=1) > dt.utcnow():
            return

        # Update timestamp
        self.last_message[(message.guild.id, message.author.id)] = dt.utcnow()

        # Add some money to the user
        amount = random.randint(3, 5)
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

    @commands.command(cls=utils.Command, aliases=['givemoney'])
    @commands.guild_only()
    async def givecoins(self, ctx:utils.Context, user:discord.Member, transfer_amount:int):
        """Give a certain amount of money to a user"""

        # Filter users
        coin_emoji = self.bot.guild_settings[ctx.guild.id].get("coin_emoji", None) or "coins"
        if transfer_amount <= 0:
            return await ctx.send("You need to give a number larger than 0.")
        if ctx.author.id == user.id:
            return await ctx.send(f"You hand your coins from one hand to the other. You did it. You gave yourself {transfer_amount:,} {coin_emoji}.")
        if user.bot:
            return await ctx.send("Bots have no need for coins, I don't think.")

        # Money handle
        async with self.bot.database() as db:
            rows = await db("SELECT * FROM user_money WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, ctx.author.id)
            try:
                amount = rows[0]['amount']
            except IndexError:
                amount = 0
            if amount < transfer_amount:
                return await ctx.send("You don't have that many coins to give.")
            await db.start_transaction()
            await db("UPDATE user_money SET amount=user_money.amount-$3 WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, ctx.author.id, transfer_amount)
            await db("UPDATE user_money SET amount=user_money.amount+$3 WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, user.id, transfer_amount)
            await db.commit_transaction()

        # Output
        return await ctx.send(f"Successfully transferred {transfer_amount:,} {coin_emoji} to {user.mention}.")


def setup(bot:utils.Bot):
    x = EconomyHandler(bot)
    bot.add_cog(x)

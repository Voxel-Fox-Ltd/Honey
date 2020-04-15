import discord
from discord.ext import commands

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

    @commands.command(cls=utils.Command)
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True, external_emojis=True)
    @commands.guild_only()
    async def createshopchannel(self, ctx:utils.Context):
        """Creates a shop channel for your server"""

        # Set up permissions
        bot_permissions = discord.PermissionOverwrite(
            read_messages=True, send_messages=True, manage_messages=True, add_reactions=True,
            manage_channels=True, embed_links=True, attach_files=True, external_emojis=True,
            manage_roles=True
        )
        everyone_permissions = discord.PermissionOverwrite(
            read_messages=False, send_messages=False, add_reactions=False,
            manage_messages=False, read_message_history=True
        )
        user_permissions = discord.PermissionOverwrite(read_messages=True)

        # Make channel with the right permissions
        overwrites = {
            ctx.guild.me: bot_permissions,
            ctx.guild.default_role: everyone_permissions,
            ctx.author: user_permissions,
        }
        shop_channel = await ctx.guild.create_text_channel("coin-shop", overwrites=overwrites)

        # Make a shop message
        coin_emoji = self.bot.guild_settings[ctx.guild.id].get("coin_emoji", None) or "coins"
        with utils.Embed() as embed:
            embed.add_field(
                "Paint (\N{LOWER LEFT PAINTBRUSH})",
                f"Paint your friends, paint your enemies. Adds a custom paint colour role to you for an hour.\n**Costs 100 {coin_emoji}**",
                inline=False,
            )
        shop_message = await shop_channel.send(embed=embed)
        await shop_message.add_reaction("\N{LOWER LEFT PAINTBRUSH}")

        # Save it all to db
        async with self.bot.database() as db:
            await db(
                """INSERT INTO shopping_channels (guild_id, channel_id, message_id) VALUES ($1, $2, $3)
                ON CONFLICT (guild_id) DO UPDATE SET channel_id=excluded.channel_id, message_id=excluded.message_id""",
                ctx.guild.id, shop_channel.id, shop_message.id
            )

        # And tell the mod it's done
        await ctx.send(f"Created new shop channel at {shop_channel.mention} - please verify the channel works before updating permissions for the everyone role.")

    @commands.command(cls=utils.Command, aliases=['inv', 'inventory'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def coins(self, ctx:utils.Context, user:discord.Member=None):
        """Gives you the content of your inventory"""

        # Grab the user
        user = user or ctx.author
        if user.id == ctx.guild.me.id:
            return await ctx.send("Obviously, I'm rich beyond belief.")
        if user.bot:
            return await ctx.send("Robots have no need for money as far as I'm aware.")

        # Get the data
        async with self.bot.database() as db:
            rows = await db("SELECT * FROM user_money WHERE guild_id=$1 AND user_id=$2", user.guild.id, user.id)

        # Throw it into an embed
        coin_emoji = self.bot.guild_settings[ctx.guild.id].get("coin_emoji", None) or "coins"
        with utils.Embed(user_random_colour=True) as embed:
            embed.set_author_to_user(user)
            embed.description = f"{rows[0]['amount']} {coin_emoji}"
        return await ctx.send(embed=embed)


def setup(bot:utils.Bot):
    x = EconomyHandler(bot)
    bot.add_cog(x)

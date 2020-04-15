import discord
from discord.ext import commands

from cogs import utils


class ShopHandler(utils.Cog):

    SHOP_ITEMS = {
        "\N{LOWER LEFT PAINTBRUSH}": ("\N{LOWER LEFT PAINTBRUSH}", "Paintbrush", 100, "Paint your friends, paint your enemies. Adds a custom paint colour role to you for an hour.", ['Paint'])
    }

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
            for emoji, (_, name, amount, description) in self.SHOP_ITEMS.items():
                embed.add_field(f"{name} ({name}) - {amount} {coin_emoji}", description, inline=False)
        shop_message = await shop_channel.send(embed=embed)
        await shop_message.add_reaction("\N{LOWER LEFT PAINTBRUSH}")

        # Save it all to db
        async with self.bot.database() as db:
            await db(
                """INSERT INTO shopping_channels (guild_id, channel_id, message_id) VALUES ($1, $2, $3)
                ON CONFLICT (guild_id) DO UPDATE SET channel_id=excluded.channel_id, message_id=excluded.message_id""",
                ctx.guild.id, shop_channel.id, shop_message.id
            )
        self.bot.guild_settings[ctx.guild.id]['shop_message_id'] = shop_message.id

        # And tell the mod it's done
        await ctx.send(f"Created new shop channel at {shop_channel.mention} - please verify the channel works before updating permissions for the everyone role.")

    @utils.Cog.listener("on_raw_reaction_add")
    async def shop_reaction_listener(self, payload:discord.RawReactionActionEvent):
        """Pinged when a user is trying to buy something from a shop"""

        # Check the reaction is on a shop message
        guild_settings = self.bot.guild_settings[payload.guild_id]
        if guild_settings['shop_message_id'] != payload.message_id:
            return
        user = self.bot.get_user(payload.user_id)
        guild = self.bot.get_guild(payload.guild_id)

        # Check the reaction they're giving
        emoji = str(payload.emoji)
        item_data = self.SHOP_ITEMS.get(emoji)

        # Not a valid reaction
        if item_data is None:
            try:
                await user.send(f"The emoji you added to the shop channel in **{guild.name}** doesn't refer to a valid shop item.")
            except (discord.Forbidden, AttributeError):
                pass
            return

        # Check their money
        db = await self.bot.database.get_connection()
        rows = await db("SELECT * FROM user_money WHERE guild_id=$1 AND user_id=$2", payload.guild_id, payload.user_id)
        if not rows or rows[0]['amount'] < item_data[2]:
            await db.disconnect()
            try:
                await user.send(f"You don't have enough to purchase a **{item_data[1]}** item in **{guild.name}**!")
            except (discord.Forbidden, AttributeError):
                pass
            return

        # Alter their inventory
        await db.start_transaction()
        await db("UPDATE user_money SET amount=amount-$3 WHERE guild_id=$1 AND user_id=$2", payload.guild_id, payload.user_id, item_data[2])
        await db(
            """INSERT INTO user_inventory (guild_id, user_id, item_name, amount)
            VALUES ($1, $2, $3, $4) ON CONFLICT (guild_id, user_id, item_name) DO UPDATE SET
            amount=user_inventory.amount+excluded.amount""",
            payload.guild_id, payload.user_id, item_data[1], 1
        )
        await db.commit_transaction()
        await db.disconnect()

        # Send them a DM
        try:
            await user.send(f"You just bought 1x **{item_data[0]}** in **{guild.name}**!")
        except (discord.Forbidden, AttributeError):
            pass
        return


def setup(bot:utils.Bot):
    x = ShopHandler(bot)
    bot.add_cog(x)

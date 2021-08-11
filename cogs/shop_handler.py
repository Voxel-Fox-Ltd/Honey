import copy

import discord
from discord.ext import commands
import voxelbotutils as vbu


class ShopHandler(vbu.Cog):

    ORIGINAL_SHOP_ITEMS = {
        "\N{LOWER LEFT PAINTBRUSH}": {
            "emoji": "\N{LOWER LEFT PAINTBRUSH}",
            "name": "Paintbrush",
            "amount": 100,  # Changed in DB but oh well
            "description": "Paint your friends, paint your enemies. Adds a custom paint colour role to you for an hour.",
            "aliases": ["Paint"],
            "price_key": "paintbrush_price",
            "quantity": 1,
        },
        "\N{CLOCK FACE ONE OCLOCK}": {
            "emoji": "\N{CLOCK FACE ONE OCLOCK}",
            "name": "Cooldown Token",
            "amount": 100,  # Changed in DB but oh well
            "description": "Gives you 100 cooldown tokens, each of which resets 1 second of your cooldown for interactions (like `hug`, `kiss`, etc).",
            "aliases": ["Cooldown Reset", "Cooldown Tokens"],
            "price_key": "cooldown_token_price",
            "quantity": 100,
        },
    }

    def get_shop_items(self, guild: discord.Guild):
        """
        Get a dict of shop items.
        """

        # See if there's a specified guild
        new_data = copy.deepcopy(self.ORIGINAL_SHOP_ITEMS)
        if guild is None:
            return new_data
        guild_settings = self.bot.guild_settings[guild.id]

        # Update original prices from cache
        for i in new_data.values():
            i['amount'] = guild_settings.get(i['price_key'], i['amount'])

        # Add the buyable roles
        buyable_roles = guild_settings.setdefault('buyable_roles', dict())
        ordered_roles = sorted(buyable_roles.keys())
        index = 0
        for role_id in ordered_roles:
            role = guild.get_role(role_id)
            if role is None:
                continue
            new_data[f"{index}\N{COMBINING ENCLOSING KEYCAP}"] = {
                "emoji": None,
                "name": "Buyable Role - " + role.name,
                "amount": buyable_roles[role_id],
                "description": f"Purchase the {role.mention} role.",
                "aliases": [],
                "price_key": None,
                "quantity": 1,
            }
            index += 1

        buyable_temporary_roles = guild_settings.setdefault('buyable_temporary_roles', dict())
        ordered_roles = sorted(buyable_temporary_roles.keys())
        for role_id in ordered_roles:
            role = guild.get_role(role_id)
            if role is None:
                continue
            new_data[f"{index}\N{COMBINING ENCLOSING KEYCAP}"] = {
                "emoji": None,
                "name": "Buyable Temporary Role - " + role.name,
                "amount": buyable_temporary_roles[role_id]['price'],
                "description": f"Purchase the {role.mention} role for {vbu.TimeValue(buyable_temporary_roles[role_id]['duration']).clean}.",
                "aliases": [],
                "price_key": None,
                "quantity": 1,
            }
            index += 1

        # Return data
        return new_data

    @vbu.command()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True, external_emojis=True, embed_links=True)
    @commands.guild_only()
    async def createshopchannel(self, ctx: vbu.Context):
        """
        Creates a shop channel for your server.
        """

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
        self.logger.info(f"Created shop channel (G{shop_channel.guild.id}/C{shop_channel.id})")

        # Make a shop message
        shop_message = await shop_channel.send("Creating shop channel...")
        self.logger.info(f"Created shop channel shop message (G{shop_channel.guild.id}/C{shop_channel.id}/M{shop_message.id})")

        # Save it all to db
        async with self.bot.database() as db:
            await db(
                """INSERT INTO guild_settings (guild_id, shop_channel_id, shop_message_id) VALUES ($1, $2, $3)
                ON CONFLICT (guild_id) DO UPDATE SET shop_channel_id=excluded.shop_channel_id, shop_message_id=excluded.shop_message_id""",
                ctx.guild.id, shop_channel.id, shop_message.id
            )
        self.bot.guild_settings[ctx.guild.id]['shop_message_id'] = shop_message.id
        self.bot.guild_settings[ctx.guild.id]['shop_channel_id'] = shop_channel.id
        self.bot.dispatch("shop_message_update", ctx.guild)

        # And tell the mod it's done
        await ctx.send(f"Created new shop channel at {shop_channel.mention} - please verify the channel works before updating permissions for the everyone role.")

    @vbu.Cog.listener("on_shop_message_update")
    async def update_shop_message(self, guild: discord.Guild):
        """
        Edit the shop message to to be pretty good.
        """

        # Get the shop message
        self.logger.info(f"Shop message update dispatched (G{guild.id})")
        try:
            shop_channel = self.bot.get_channel(self.bot.guild_settings[guild.id]['shop_channel_id'])
            shop_message = await shop_channel.fetch_message(self.bot.guild_settings[guild.id]['shop_message_id'])
            if shop_message is None:
                self.logger.info(f"Can't update shop message - no message found (G{guild.id})")
                raise AttributeError()
        except (discord.NotFound, AttributeError):
            self.logger.info(f"Can't update shop message - no message/channel found (G{guild.id})")
            return

        # Generate embed
        coin_emoji = self.bot.guild_settings[guild.id].get("coin_emoji", None) or "coins"
        buttons = []
        with vbu.Embed() as embed:
            for emoji, data in self.get_shop_items(guild).items():
                item_price = self.bot.guild_settings[guild.id].get(data['price_key'], data['amount'])
                if item_price <= 0:
                    continue
                embed.add_field(f"{data['name']} ({emoji}) - {item_price} {coin_emoji}", data['description'], inline=False)
                buttons.append(vbu.Button(label=data['name'], emoji=emoji, custom_id="SHOP_PURCHASE"))

        # See if we need to edit the message
        try:
            current_embed = shop_message.embeds[0]
        except IndexError:
            current_embed = None
        if embed == current_embed:
            self.logger.info(f"Not updating shop message - no changes presented (G{guild.id})")
            return

        # Edit message
        self.logger.info(f"Updating shop message (G{guild.id})")
        await shop_message.edit(
            content=None,
            embed=embed,
            components=vbu.MessageComponents.add_buttons_with_rows(*buttons),
        )

    # @vbu.Cog.listener("on_raw_reaction_clear")
    # async def shop_reaction_clear_listener(self, payload: discord.RawReactionClearEvent):
    #     """
    #     Pinged when all reactions are cleared from a shop message.
    #     """

    #     guild_settings = self.bot.guild_settings[payload.guild_id]
    #     if guild_settings['shop_message_id'] != payload.message_id:
    #         return
    #     channel = self.bot.get_channel(payload.channel_id)
    #     try:
    #         message = await channel.fetch_message(payload.message_id)
    #     except (discord.Forbidden, discord.NotFound, discord.HTTPException):
    #         return
    #     for emoji in self.get_shop_items(self.bot.get_guild(payload.guild_id)).keys():
    #         await message.add_reaction(emoji)

    @vbu.Cog.listener("on_raw_reaction_add")
    async def shop_reaction_listener(self, payload: discord.RawReactionActionEvent):
        """
        Pinged when a user is trying to buy something from a shop.
        """

        # Check the reaction is on a shop message
        guild_settings = self.bot.guild_settings[payload.guild_id]
        if guild_settings['shop_message_id'] != payload.message_id:
            return
        guild = self.bot.get_guild(payload.guild_id) or await self.bot.fetch_guild(payload.guild_id)
        user = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
        if user.bot:
            return
        channel = self.bot.get_channel(payload.channel_id)

        # Check the reaction they're giving
        emoji = str(payload.emoji)
        item_data = self.get_shop_items(guild).get(emoji)

        # Try and remove the reaction
        try:
            message = await channel.fetch_message(payload.message_id)
            if item_data:
                await message.remove_reaction(payload.emoji, user)
            else:
                await message.clear_reactions()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass

        # Not a valid reaction
        if item_data is None or self.bot.guild_settings[payload.guild_id].get(item_data['price_key'], item_data['amount']) <= 0:
            try:
                await user.send(f"The emoji you added to the shop channel in **{guild.name}** doesn't refer to a valid shop item.")
            except (discord.Forbidden, AttributeError):
                pass
            self.logger.info(f"Invalid reaction on shop message (G{payload.guild_id}/C{payload.channel_id}/U{payload.user_id}/E{payload.emoji!s})")
            return

        # Get the item price
        item_price = self.bot.guild_settings[payload.guild_id].get(item_data['price_key'], item_data['amount'])
        if item_price <= 0:
            return

        # Check their money
        db = await self.bot.database.get_connection()
        rows = await db("SELECT * FROM user_money WHERE guild_id=$1 AND user_id=$2", payload.guild_id, payload.user_id)
        if not rows or rows[0]['amount'] < item_price:
            await db.disconnect()  # TODO get amount from guild settings
            try:
                await user.send(f"You don't have enough to purchase a **{item_data['name']}** item in **{guild.name}**!")
            except (discord.Forbidden, AttributeError):
                pass
            self.logger.info(f"User unable to purchase item (G{payload.guild_id}/C{payload.channel_id}/U{payload.user_id}/E{payload.emoji!s})")
            return

        # Alter their inventory
        await db.start_transaction()
        await db("UPDATE user_money SET amount=user_money.amount-$3 WHERE guild_id=$1 AND user_id=$2", guild.id, user.id, item_price)
        await db("UPDATE user_money SET amount=user_money.amount+$3 WHERE guild_id=$1 AND user_id=$2", guild.id, guild.me.id, item_price)
        await db(
            """INSERT INTO user_inventory (guild_id, user_id, item_name, amount)
            VALUES ($1, $2, $3, $4) ON CONFLICT (guild_id, user_id, item_name) DO UPDATE SET
            amount=user_inventory.amount+excluded.amount""",
            payload.guild_id, payload.user_id, item_data['name'], item_data['quantity']
        )
        await db.commit_transaction()
        await db.disconnect()

        # Send them a DM
        try:
            guild_prefix = self.bot.guild_settings[payload.guild_id].get("prefix")
            await user.send(f"You just bought {item_data['quantity']}x **{item_data['emoji'] or item_data['name']}** in **{guild.name}**! You can use it with the `{guild_prefix}use {item_data['name'].lower().replace(' ', '')}` command.")
        except (discord.Forbidden, AttributeError):
            pass
        self.logger.info(f"User successfully purchased item (G{payload.guild_id}/C{payload.channel_id}/U{payload.user_id}/E{payload.emoji!s})")
        return

    @vbu.Cog.listener("on_component_interaction")
    async def shop_button_listener(self, payload: vbu.ComponentInteractionPayload):
        """
        Pinged when a user is trying to buy something from a shop.
        """

        if payload.component.custom_id != "SHOP_PURCHASE":
            return

        # Check the reaction is on a shop message
        guild_settings = self.bot.guild_settings[payload.guild.id]
        if guild_settings['shop_message_id'] != payload.message.id:
            return
        guild = payload.guild
        user = payload.user
        channel = payload.channel

        # Check the reaction they're giving
        emoji = str(payload.component.emoji)
        item_data = self.get_shop_items(guild).get(emoji)

        # Not a valid reaction
        if item_data is None or self.bot.guild_settings[guild.id].get(item_data['price_key'], item_data['amount']) <= 0:
            try:
                await payload.send(f"The emoji you added to the shop channel in **{guild.name}** doesn't refer to a valid shop item.", ephemeral=True)
            except (discord.Forbidden, AttributeError):
                pass
            self.logger.info(f"Invalid reaction on shop message (G{payload.guild_id}/C{payload.channel_id}/U{payload.user_id}/E{payload.emoji!s})")
            return

        # Get the item price
        item_price = self.bot.guild_settings[payload.guild_id].get(item_data['price_key'], item_data['amount'])
        if item_price <= 0:
            return

        # Check their money
        db = await self.bot.database.get_connection()
        rows = await db("SELECT * FROM user_money WHERE guild_id=$1 AND user_id=$2", payload.guild_id, payload.user_id)
        if not rows or rows[0]['amount'] < item_price:
            await db.disconnect()  # TODO get amount from guild settings
            try:
                await payload.send(f"You don't have enough to purchase a **{item_data['name']}** item!", ephemeral=True)
            except (discord.Forbidden, AttributeError):
                pass
            self.logger.info(f"User unable to purchase item (G{payload.guild_id}/C{payload.channel_id}/U{payload.user_id}/E{payload.emoji!s})")
            return

        # Alter their inventory
        await db.start_transaction()
        await db("UPDATE user_money SET amount=user_money.amount-$3 WHERE guild_id=$1 AND user_id=$2", guild.id, user.id, item_price)
        await db("UPDATE user_money SET amount=user_money.amount+$3 WHERE guild_id=$1 AND user_id=$2", guild.id, guild.me.id, item_price)
        await db(
            """INSERT INTO user_inventory (guild_id, user_id, item_name, amount)
            VALUES ($1, $2, $3, $4) ON CONFLICT (guild_id, user_id, item_name) DO UPDATE SET
            amount=user_inventory.amount+excluded.amount""",
            payload.guild_id, payload.user_id, item_data['name'], item_data['quantity']
        )
        await db.commit_transaction()
        await db.disconnect()

        # Send them a DM
        try:
            guild_prefix = self.bot.guild_settings[payload.guild_id].get("prefix")
            await payload.send(
                (
                    f"You just bought {item_data['quantity']}x **{item_data['emoji'] or item_data['name']}**! "
                    f"You can use it with the `{guild_prefix}use {item_data['name'].lower().replace(' ', '')}` command."
                ),
                ephemeral=True,
            )
        except (discord.Forbidden, AttributeError):
            pass
        self.logger.info(f"User successfully purchased item (G{payload.guild_id}/C{payload.channel_id}/U{payload.user_id}/E{payload.emoji!s})")
        return


def setup(bot: vbu.Bot):
    x = ShopHandler(bot)
    bot.add_cog(x)

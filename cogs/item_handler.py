import random
import typing
from datetime import datetime as dt, timedelta

import discord
from discord.ext import commands

from cogs import utils


class ItemHandler(utils.Cog):

    @commands.command(cls=utils.Command, aliases=['inv', 'inventory', 'money'])
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
            coin_rows = await db("SELECT * FROM user_money WHERE guild_id=$1 AND user_id=$2", user.guild.id, user.id)
            inv_rows = await db("SELECT * FROM user_inventory WHERE guild_id=$1 AND user_id=$2", user.guild.id, user.id)

        # Throw it into an embed
        coin_emoji = self.bot.guild_settings[ctx.guild.id].get("coin_emoji", None) or "coins"
        with utils.Embed(use_random_colour=True) as embed:
            embed.set_author_to_user(user)
            inventory_string_rows = []
            for row in inv_rows:
                if row['amount'] == 0:
                    continue
                item_data = [i for i in self.bot.get_cog("ShopHandler").SHOP_ITEMS.values() if i[1] == row['item_name']][0]
                inventory_string_rows.append(f"{row['amount']}x {item_data[0] or item_data[1]}")
            embed.description = f"**{coin_rows[0]['amount']:,} {coin_emoji}**\n" + "\n".join(inventory_string_rows)
        return await ctx.send(embed=embed)

    @commands.command(cls=utils.Command, aliases=['use'])
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @commands.guild_only()
    async def useitem(self, ctx:utils.Context, item_name:str, user:typing.Optional[discord.Member]):
        """Use an item that you purchased from the shop"""

        # Get the items they own
        try:
            item_data = [i for i in self.bot.get_cog("ShopHandler").SHOP_ITEMS.values() if item_name.lower() == i[1].lower() or item_name.lower() in [o.lower() for o in i[4]]][0]
        except IndexError:
            return await ctx.send("That isn't an item that exists.")
        db = await self.bot.database.get_connection()
        rows = await db(
            "SELECT * FROM user_inventory WHERE guild_id=$1 AND user_id=$2 AND LOWER(item_name)=LOWER($3)",
            ctx.guild.id, ctx.author.id, item_data[1],
        )
        if not rows:
            await ctx.send(f"You don't have any **{item_name}** items in this server.")
            await db.disconnect()
            return

        # Use the item
        user = user or ctx.author

        # Paint
        if item_data[1] == "Paintbrush":

            # See if there's a valid role position
            guild_settings = self.bot.guild_settings[ctx.guild.id]
            role_position_role_id = guild_settings.get('custom_role_position_id')
            role_position = ctx.guild.get_role(role_position_role_id)
            if role_position is None:
                await db.disconnect()
                return await ctx.send(f"This item can't be used unless the custom role position is set (`{ctx.prefix}setup`).")

            # Get a random role colour
            colour_name, colour_value = random.choice(list(utils.colour_names.COLOURS_BY_NAME.items()))

            # See if there's any point
            upper_roles = [i for i in user.roles if i.position >= role_position.position and i.colour.value > 0]
            if upper_roles:
                await db.disconnect()
                return await ctx.send("There's no point in painting that user - they have coloured roles above the paint role positions.")

            # Make a role
            try:
                role: discord.Role = await ctx.guild.create_role(
                    name=colour_name.title(), colour=discord.Colour(colour_value), reason="Paintbrush used"
                )
            except discord.Forbidden:
                await db.disconnect()
                return await ctx.send("I couldn't make a new colour role for you.")

            # Update its position
            try:
                await role.edit(position=role_position.position - 1)
            except discord.HTTPException as e:
                self.logger.error(e)

            # Add it to the user
            try:
                await user.add_roles(role, reason="Paintbrush used")
            except discord.Forbidden:
                await db.disconnect()
                return await ctx.send("I created the paint role, but I couldn't add it to you.")

            # Add to database as a temporary role
            await db(
                "INSERT INTO temporary_roles (guild_id, user_id, role_id, remove_timestamp, delete_role) VALUES ($1, $2, $3, $4, true)",
                ctx.guild.id, user.id, role.id, dt.utcnow() + timedelta(hours=1),
            )
            await ctx.send(f"Painted {user.mention} with {role.mention}!")

        # It's nothing else
        else:
            await db.disconnect()
            return

        # Alter their inventory
        await db(
            "UPDATE user_inventory SET amount=user_inventory.amount-1 WHERE guild_id=$1 AND user_id=$2 AND item_name=$3",
            ctx.guild.id, ctx.author.id, item_data[1],
        )
        await db.disconnect()


def setup(bot:utils.Bot):
    x = ItemHandler(bot)
    bot.add_cog(x)

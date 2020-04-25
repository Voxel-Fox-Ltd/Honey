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
        if not rows or rows[0]['amount'] <= 0:
            await ctx.send(f"You don't have any **{item_name}** items in this server.")
            await db.disconnect()
            return

        # Use the item
        user = user or ctx.author
        await ctx.trigger_typing()

        # Paint
        if item_data[1] == "Paintbrush":

            # See if there's a valid role position
            guild_settings = self.bot.guild_settings[ctx.guild.id]
            role_position_role_id = guild_settings.get('custom_role_position_id')
            try:
                role_position_role = [i for i in await ctx.guild.fetch_roles() if i.id == role_position_role_id][0]
                # role_position_role = ctx.guild.get_role(role_position_role_id)
                # if role_position_role is None:
                #     raise IndexError()
            except IndexError:
                await db.disconnect()
                return await ctx.send(f"This item can't be used unless the custom role position is set (`{ctx.prefix}setup`).")
            position = role_position_role.position

            # Get a random role colour
            colour_name, colour_value = random.choice(list(utils.colour_names.COLOURS_BY_NAME.items()))

            # See if there's any point
            upper_roles = [i for i in user.roles if i.position >= position and i.colour.value > 0]
            if upper_roles:
                await db.disconnect()
                self.logger.info(f"Not painting user (G{user.guild.id}/U{user.id}) due to higher roles - {upper_roles}")
                return await ctx.send("There's no point in painting that user - they have coloured roles above the paint role positions.")

            # Make a role
            try:
                role = await ctx.guild.create_role(
                    name=colour_name.title(), colour=discord.Colour(colour_value), reason="Paintbrush used"
                )
                self.logger.info(f"Created paint role in guild (G{ctx.guild.id}/R{role.id})")
            except discord.Forbidden:
                await db.disconnect()
                self.logger.error(f"Couldn't create paint role, forbidden (G{ctx.guild.id}/U{ctx.author.id})")
                return await ctx.send("I couldn't make a new colour role for you - missing permissions.")
            except discord.HTTPException as e:
                await db.disconnect()
                self.logger.error(f"Couldn't create paint role (G{ctx.guild.id}/U{ctx.author.id}) - {e}")
                await role.delete(reason="Messed up making paint role")
                return await ctx.send(f"I couldn't make a new colour role for you - I think we hit the role limit?")

            # Fetch all the roles from the API
            await ctx.guild.fetch_roles()  # TODO this only needs to exist until roles are cached on creation

            # Edit the role position
            try:
                self.logger.info(f"Moving role {role.id} to position {position - 1} (my highest is {role.guild.me.top_role.position})")
                await role.edit(position=position - 1, reason="Update positioning")
                self.logger.info(f"Edited paint role position in guild (G{ctx.guild.id}/R{role.id})")
            except discord.Forbidden:
                await db.disconnect()
                self.logger.error(f"Couldn't move paint role, forbidden (G{ctx.guild.id}/U{ctx.author.id})")
                return await ctx.send("I couldn't move the new colour role position - missing permissions.")
            except discord.HTTPException as e:
                await db.disconnect()
                self.logger.error(f"Couldn't move paint role (G{ctx.guild.id}/U{ctx.author.id}) - {e}")
                await role.delete(reason="Messed up making paint role")
                return await ctx.send(f"I couldn't move the new paint role - {e}")

            # Add it to the user
            try:
                await user.add_roles(role, reason="Paintbrush used")
                self.logger.info(f"Add paint role to user (G{ctx.guild.id}/R{role.id}/U{user.id})")
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
        self.logger.info(f"Remove item ({item_data[1]}) from user (G{ctx.guild.id}/U{ctx.author.id})")
        await db.disconnect()


def setup(bot:utils.Bot):
    x = ItemHandler(bot)
    bot.add_cog(x)

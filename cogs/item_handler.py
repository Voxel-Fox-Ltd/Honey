import random
import typing
from datetime import datetime as dt, timedelta
import asyncio

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
            success = await self.use_paintbrush(ctx, db=db, user=user)
            if success is False:
                await db.disconnect()
                return

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

    async def use_paintbrush(self, ctx:utils.Context, db:utils.DatabaseConnection, user:discord.Member):
        """Use the paintbrush on a user in a given server"""

        # See if there's a valid role position
        guild_settings = self.bot.guild_settings[ctx.guild.id]
        role_position_role_id = guild_settings.get('custom_role_position_id')
        role_position_role = ctx.guild.get_role(role_position_role_id)
        if role_position_role is None:
            await ctx.send(f"This item can't be used unless the custom role position is set (`{ctx.prefix}setup`).")
            return False
        visibility_position = role_position_role.position  # This is the position we want the role to be at when it's made

        # See if there's any point
        upper_roles = [i for i in user.roles if i.position >= visibility_position and i.colour.value > 0]
        if upper_roles:
            self.logger.info(f"Not painting user (G{user.guild.id}/U{user.id}) due to higher roles - {upper_roles}")
            await ctx.send("There's no point in painting that user - they have coloured roles above the paint role positions.")
            return False

        # Get a random role colour
        colour_name, colour_value = random.choice(list(utils.colour_names.COLOURS_BY_NAME.items()))

        # See if they have a paint role already
        paint_rows = await db(
            "SELECT * FROM temporary_roles WHERE guild_id=$1 AND user_id=$2 AND key='Paint'",
            ctx.guild.id, user.id
        )
        role = None
        if paint_rows:
            role = ctx.guild.get_role(paint_rows[0]['role_id'])

        # Make a role
        role_kwargs = dict(name=colour_name.title(), colour=discord.Colour(colour_value), reason="Paintbrush used")
        role_created = False
        try:
            if role is None:
                role = await ctx.guild.create_role(**role_kwargs)
                role_created = True
                self.logger.info(f"Created paint role in guild (G{ctx.guild.id}/R{role.id})")
            else:
                await role.edit(**role_kwargs)
                self.logger.info(f"Updated paint role in guild (G{ctx.guild.id}/R{role.id})")
        except discord.Forbidden:
            self.logger.error(f"Couldn't create paint role, forbidden (G{ctx.guild.id}/U{ctx.author.id})")
            await ctx.send("I couldn't make a new colour role for you - missing permissions.")
            return False
        except discord.HTTPException as e:
            self.logger.error(f"Couldn't create paint role (G{ctx.guild.id}/U{ctx.author.id}) - {e}")
            try:
                await role.delete(reason="Messed up making paint role")
            except discord.NotFound:
                pass
            await ctx.send(f"I couldn't make a new colour role for you - I think we hit the role limit?")
            return False

        # Update the role position if a new role was created
        if role_created:

            # Sleep a lil so we can get teh cache to update
            self.logger.info(f"Sleeping before updating role position... (G{ctx.guild.id})")
            await asyncio.sleep(1)
            role_position_role = ctx.guild.get_role(role_position_role_id)

            # Edit the role position
            try:
                self.logger.info(f"Moving role {role.id} to position {role_position_role.position - 1} (my highest is {role.guild.me.top_role.position})")
                await role.edit(position_below=role_position_role, reason="Update positioning")
                self.logger.info(f"Edited paint role position in guild (G{ctx.guild.id}/R{role.id})")
            except discord.Forbidden:
                self.logger.error(f"Couldn't move paint role, forbidden (G{ctx.guild.id}/U{ctx.author.id})")
                await ctx.send("I couldn't move the new colour role position - missing permissions.")
                return False
            except discord.HTTPException as e:
                self.logger.error(f"Couldn't move paint role (G{ctx.guild.id}/U{ctx.author.id}) - {e}")
                await role.delete(reason="Messed up making paint role")
                await ctx.send(f"I couldn't move the new paint role - {e}")
                return False

        # Add it to the user
        if role_created:
            try:
                await user.add_roles(role, reason="Paintbrush used")
                self.logger.info(f"Add paint role to user (G{ctx.guild.id}/R{role.id}/U{user.id})")
            except discord.Forbidden:
                await ctx.send("I created the paint role, but I couldn't add it to you.")
                return False

        # Add to database
        if role_created:
            await db(
                """INSERT INTO temporary_roles (guild_id, user_id, role_id, remove_timestamp, delete_role, key, dm_user)
                VALUES ($1, $2, $3, $4, true, 'Paint', true)""",
                ctx.guild.id, user.id, role.id, dt.utcnow() + timedelta(hours=1),
            )
        else:
            await db(
                """UPDATE temporary_roles SET remove_timestamp=$4 WHERE
                guild_id=$1 AND user_id=$2 AND role_id=$3 AND key='Paint'""",
                ctx.guild.id, user.id, role.id, dt.utcnow() + timedelta(hours=1),
            )
        await ctx.send(
            f"Painted {user.mention} with {role.mention}!",
            allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False)
        )
        return True


def setup(bot:utils.Bot):
    x = ItemHandler(bot)
    bot.add_cog(x)

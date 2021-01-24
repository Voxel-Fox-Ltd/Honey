import random
import re
import typing
from datetime import datetime as dt, timedelta
import asyncio
import copy
import collections

import discord
from discord.ext import commands
import voxelbotutils as utils

from cogs import utils as localutils


class ItemHandler(utils.Cog):

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.paintbrush_locks: typing.Dict[int, asyncio.Lock] = collections.defaultdict(asyncio.Lock)  # guild_id: Lock

    @commands.command(cls=utils.Command, aliases=['inv', 'inventory', 'money'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def coins(self, ctx:utils.Context, user:discord.Member=None):
        """
        Gives you the content of your inventory.
        """

        # Make sure there's money set up
        if self.bot.guild_settings[ctx.guild.id].get('shop_message_id') is None:
            return await ctx.send("There's no shop set up for this server, so there's no point in you getting money. Sorry :/")

        # Grab the user
        user = user or ctx.author
        if user.id == ctx.guild.me.id:
            return await ctx.send("Obviously, I'm rich beyond belief.")
        if user.bot:
            return await ctx.send("Robots have no need for money as far as I'm aware.")

        # Get the data
        async with self.bot.database() as db:
            coin_rows = await db("SELECT * FROM user_money WHERE guild_id=$1 AND user_id=$2", user.guild.id, user.id)
            if not coin_rows:
                coin_rows = [{'amount': 0}]
            inv_rows = await db("SELECT * FROM user_inventory WHERE guild_id=$1 AND user_id=$2", user.guild.id, user.id)

        # Throw it into an embed
        coin_emoji = self.bot.guild_settings[ctx.guild.id].get("coin_emoji", None) or "coins"
        with utils.Embed(use_random_colour=True) as embed:
            embed.set_author_to_user(user)
            inventory_string_rows = []
            for row in inv_rows:
                if row['amount'] == 0:
                    continue
                try:
                    item_data = [i for i in self.bot.get_cog("ShopHandler").get_shop_items(ctx.guild).values() if i['name'] == row['item_name']][0]
                except IndexError:
                    continue
                inventory_string_rows.append(f"{row['amount']}x {item_data['emoji'] or item_data['name']}")
            embed.description = f"**{coin_rows[0]['amount']:,} {coin_emoji}**\n" + "\n".join(inventory_string_rows)
        return await ctx.send(embed=embed)

    @utils.command(aliases=['use'])
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @commands.guild_only()
    async def useitem(self, ctx:utils.Context, item_name:str, user:typing.Optional[discord.Member], *, args:str=None):
        """
        Use an item that you purchased from the shop.
        """

        # Get the items they own
        try:
            item_data = [i for i in self.bot.get_cog("ShopHandler").get_shop_items(ctx.guild).values() if item_name.lower().replace(' ', '') == i['name'].lower().replace(' ', '') or item_name.lower().replace(' ', '') in [o.lower().replace(' ', '') for o in i['aliases']]][0]
        except IndexError:
            return await ctx.send("That isn't an item that exists.")
        db = await self.bot.database.get_connection()
        rows = await db(
            "SELECT * FROM user_inventory WHERE guild_id=$1 AND user_id=$2 AND LOWER(item_name)=LOWER($3)",
            ctx.guild.id, ctx.author.id, item_data['name'],
        )
        if (not rows or rows[0]['amount'] <= 0) and ctx.original_author_id not in self.bot.owner_ids:
            await ctx.send(f"You don't have any **{item_data['name']}** items in this server.")
            await db.disconnect()
            return

        # Use the item
        user = user or ctx.author
        await ctx.trigger_typing()

        # Paint
        if item_data['name'] == 'Paintbrush':
            async with self.paintbrush_locks[ctx.guild.id]:
                data = await self.use_paintbrush(ctx, args, db=db, user=user)

        # Cooldown tokens
        elif item_data['name'] == 'Cooldown Token':
            data = await self.use_cooldown_token(ctx, db=db, user=user)

        # Cooldown tokens
        elif item_data['name'].startswith('Buyable Role'):
            role_search = re.search(r"<@&(?P<roleid>[0-9]{13,23})", item_data['description'])
            role_id = role_search.group("roleid")
            self.logger.info(role_id)
            try:
                await ctx.author.add_roles(ctx.guild.get_role(int(role_id)), reason="Role purchased")
            except Exception as e:
                await ctx.send(f"I couldn't add the role - {e}")
                data = False
            else:
                await ctx.send("Added role.")
                data = True

        # Cooldown tokens
        elif item_data['name'].startswith('Buyable Temporary Role'):
            role_search = re.search(r"<@&(?P<roleid>[0-9]{13,23})", item_data['description'])
            role_id = role_search.group("roleid")
            self.logger.info(role_id)
            try:
                await ctx.author.add_roles(ctx.guild.get_role(int(role_id)), reason="Role purchased")
            except Exception as e:
                await ctx.send(f"I couldn't add the role - {e}")
                data = False
            else:
                await ctx.send("Added role.")
                duration_rows = await db("SELECT * FROM buyable_temporary_roles WHERE guild_id=$1 AND role_id=$2", ctx.guild.id, int(role_id))
                await db(
                    """INSERT INTO temporary_roles (guild_id, role_id, user_id, remove_timestamp, key, dm_user)
                    VALUES ($1, $2, $3, $4, 'Buyable Temp Role', true) ON CONFLICT (guild_id, role_id, user_id) DO UPDATE
                    SET remove_timestamp=excluded.remove_timestamp, key=excluded.key, dm_user=excluded.dm_user""",
                    ctx.guild.id, int(role_id), ctx.author.id, dt.utcnow() + utils.TimeValue(duration_rows[0]['duration']).delta
                )
                data = True

        # It's nothing else
        else:
            await ctx.send("No use method set in the code for that item.")
            await db.disconnect()
            return

        # Unpack data
        try:
            success, amount = data
        except TypeError:
            success, amount = data, 1

        # Disconnect from the DB if the item failed
        if success is False:
            await db.disconnect()
            return

        # Alter their inventory
        await db(
            "UPDATE user_inventory SET amount=user_inventory.amount - $4 WHERE guild_id=$1 AND user_id=$2 AND item_name=$3",
            ctx.guild.id, ctx.author.id, item_data['name'], amount
        )
        self.logger.info(f"Remove item ({item_data['name']}) from user (G{ctx.guild.id}/U{ctx.author.id})")
        await db.disconnect()

    @utils.command(aliases=['paintbrush'])
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @commands.guild_only()
    async def paint(self, ctx:utils.Context, user:typing.Optional[discord.Member], *, args:str=None):
        """
        Use the paintbrush on a user in a given server.
        """

        await ctx.invoke(self.bot.get_command("use"), item_name="paintbrush", user=user or ctx.author, args=args)

    @utils.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @commands.guild_only()
    async def multipaint(self, ctx:utils.Context, users:commands.Greedy[discord.Member], *, args:str=None):
        """
        Use the paintbrush on a user in a given server.
        """

        if not users:
            raise utils.errors.MissingRequiredArgumentString("users")
        if len(users) > 5:
            return await ctx.send("You can only multipaint 5 users at once.")
        for u in users:
            await ctx.invoke(self.bot.get_command("use"), item_name="paintbrush", user=u, args=args)

    async def use_paintbrush(self, ctx:utils.Context, args:str, db:utils.DatabaseConnection, user:discord.Member):
        """
        Use the paintbrush on a user in a given server.
        """

        # See if there's a valid role position
        guild_settings = self.bot.guild_settings[ctx.guild.id]
        role_position_role_id = guild_settings.get('custom_role_position_id')
        guild_roles = {r.id: r for r in await ctx.guild.fetch_roles()}
        role_position_role = guild_roles.get(role_position_role_id)
        if role_position_role is None:
            await ctx.send(f"This item can't be used unless the custom role position is set (`{ctx.prefix}setup`).")
            return False

        if user.id != ctx.author.id:

            # See if the author has paint disabled
            if self.bot.user_settings[ctx.author.id]['allow_paint'] is False and ctx.author.id not in self.bot.owner_ids:
                await ctx.send("You can't paint other users while you have paint disabled yourself.")
                return False

            # See if the target has paint disabled
            if self.bot.user_settings[user.id]['allow_paint'] is False and ctx.author.id not in self.bot.owner_ids:
                await ctx.send(f"{user.mention} has paint disabled.", allowed_mentions=discord.AllowedMentions(users=False))
                return False

        # See if there's any point
        upper_roles = [i for i in [o.id for o in user.roles] if guild_roles[i] >= role_position_role and guild_roles[i].colour.value > 0]
        if upper_roles:
            self.logger.info(f"Not painting user (G{user.guild.id}/U{user.id}) due to higher roles - {upper_roles}")
            await ctx.send("There's no point in painting that user - they have coloured roles above the paint role positions.")
            return False

        # Get a random role colour
        colour_name, colour_value = None, None
        if args:
            try:
                colour = await utils.converters.ColourConverter(allow_default_colours=False).convert(ctx, args)
                colour_name, colour_value = args.strip(), colour.value
            except commands.BadArgument:
                await ctx.send(f"`{args.title()}` isn't a valid colour name.", allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False))
                return False
        if colour_name is None:
            colour_name, colour_value = random.choice(list(utils.converters.ColourConverter.COLOURS_BY_NAME.items()))

        # See if they have a paint role already
        paint_rows = await db(
            "SELECT * FROM temporary_roles WHERE guild_id=$1 AND user_id=$2 AND key='Paint'",
            ctx.guild.id, user.id
        )
        role = None
        if paint_rows:
            role = ctx.guild.get_role(paint_rows[0]['role_id'])

        # Make a role
        role_kwargs = dict(name=colour_name.title() + " (Paint)", colour=discord.Colour(colour_value), reason="Paintbrush used")
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
            await ctx.send("I couldn't make a new colour role for you - I think we hit the role limit?")
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
                await localutils.move_role_position_below(role, role_position_role, reason="Update positioning")
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
        if role not in user.roles:
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
            f"Painted {user.mention} with **{' '.join(role.name.split(' ')[:-1])}**!",
            allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False)
        )
        return True

    @utils.command(aliases=['colorsearch'])
    async def coloursearch(self, ctx:utils.Context, *, search:str):
        """
        Searches for a colour by a given name.
        """

        valid_colours = []
        for name, value in utils.converters.ColourConverter.COLOURS_BY_NAME.items():
            if search.lower() in name.lower():
                valid_colours.append((name, value))
        valid_colours = sorted(valid_colours)
        if not valid_colours:
            return await ctx.send(f"No colours matching `{search}` could be found.", allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False))
        valid_string = [f"{i.title()}: `#{hex(o)[2:]}`" for i, o in valid_colours[:10]]
        return await ctx.send(f"Showing {len(valid_string)} of {len(valid_colours)} matching colours:\n" + '\n'.join(valid_string))

    @utils.command()
    @commands.is_owner()  # TODO update this
    async def setpainttimeout(self, ctx:utils.Context, user:discord.Member, duration:utils.TimeValue):
        """
        Set the paint timeout for a given user to an abritrary value.
        """

        async with self.bot.database() as db:
            await db(
                """UPDATE temporary_roles SET remove_timestamp=$3 WHERE
                guild_id=$1 AND user_id=$2 AND key='Paint'""",
                ctx.guild.id, user.id, dt.utcnow() + duration.delta,
            )
        return await ctx.send("Updated.")

    async def use_cooldown_token(self, ctx:utils.Context, db:utils.DatabaseConnection, user:discord.Member):
        """
        Use the cooldown token on a user in a given server.
        """

        # Get cooldown for user
        new_ctx = copy.copy(ctx)
        new_ctx.message.author = user or ctx.author
        interaction = self.bot.get_command("interaction_command_meta")
        remaining_time = interaction.get_remaining_cooldown(ctx)

        # See if they actually have a cooldown to use
        if remaining_time is None or remaining_time <= 3:
            await ctx.send("Your cooldown is already at 0.")
            return False
        remaining_time = int(remaining_time)

        # See how many tokens they have
        token_count_rows = await db(
            "SELECT * FROM user_inventory WHERE user_id=$1 AND guild_id=$2 AND item_name='Cooldown Token'",
            ctx.author.id, ctx.guild.id,
        )
        token_count = token_count_rows[0]['amount']

        # See how many tokens they gonna use
        used_tokens = min([token_count, remaining_time])

        # Use the tokens
        bucket: utils.cooldown.Cooldown = interaction._buckets.get_bucket(new_ctx.message)
        bucket._last = bucket._last - used_tokens
        bucket._window = bucket._last - used_tokens
        interaction._buckets._cache[interaction._buckets._bucket_key(new_ctx.message)] = bucket

        # Output to user
        await ctx.send(
            f"Reset {used_tokens} seconds of {user.mention}'s cooldown, leaving you with {token_count - used_tokens} cooldown tokens remaining.",
            allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False)
        )
        return True, used_tokens


def setup(bot:utils.Bot):
    x = ItemHandler(bot)
    bot.add_cog(x)

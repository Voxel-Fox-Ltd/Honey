import typing
import asyncio

import discord
from discord.ext import commands
import voxelbotutils as utils

from cogs import utils as localutils


class CustomRoleHandler(utils.Cog):

    @utils.group()
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def customrole(self, ctx:utils.Context):
        """
        The parent command to manage your custom role.
        """

        # See if we invoke a real command
        if ctx.invoked_subcommand is not None:
            return

        # Throw em some help
        return await ctx.send(f"This command is used so you can manage your custom role on this server, should you have one. See `{ctx.prefix}help {ctx.invoked_with}` to learn more.")

    async def check_for_custom_role(self, member:discord.Member) -> typing.Optional[discord.Role]:
        """
        Returns the user's custom role object for the server, or None if they
        don't have one. This does NOT check for whether they can/cannot have one.
        """

        async with self.bot.database() as db:
            rows = await db("SELECT * FROM custom_roles WHERE guild_id=$1 AND user_id=$2", member.guild.id, member.id)
        if not rows:
            return None
        return member.guild.get_role(rows[0]['role_id'])

    @utils.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        """
        Delete a custom role when the user leaves the guild.
        """

        role = await self.check_for_custom_role(member)
        if role is None:
            return
        try:
            await role.delete(reason="Member left server")
        except discord.HTTPException:
            pass

    @utils.Cog.listener()
    async def on_member_update(self, before:discord.Member, member:discord.Member):
        """
        Listens for members losing the required custom role master, and thus deletes the custom role.
        """

        # Check the custom role
        master_role_id = self.bot.guild_settings[member.guild.id].get('custom_role_id')
        if master_role_id is None:
            return  # No set custom role
        master_role = member.guild.get_role(master_role_id)
        if master_role is None:
            return  # Custom role master was deleted

        # See if they HAD the custom role master
        if master_role not in before.roles:
            return

        # See if they still HAVE the custom role master
        if master_role in member.roles:
            return

        # They lost the custom role master - delete their custom role
        role = await self.check_for_custom_role(member)
        if role is None:
            return
        try:
            await role.delete(reason="Member no longer has the custom role master")
        except discord.HTTPException:
            pass

    @customrole.command(cls=utils.Command)
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @utils.cooldown.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def name(self, ctx:utils.Context, *, name:commands.clean_content):
        """
        Change the name of your custom role.
        """

        # Get their role
        role = await self.check_for_custom_role(ctx.author)
        if role is None:
            return await ctx.send(f"You don't have a custom role on this server - set one with `{ctx.prefix}{ctx.command.parent.name} create`.")

        # Edit name
        try:
            role_xfix = self.bot.guild_settings[ctx.guild.id].get('custom_role_xfix', None) or '(Custom)'
            if role_xfix.endswith(':'):
                role_name = f"{role_xfix.strip(':')} {name.strip()}"
            else:
                role_name = f"{name.strip()} {role_xfix.strip(':')}"
            await role.edit(name=role_name)
            self.logger.info(f"Changed the name of a custom role to '{name}' (G{ctx.guild.id}/R{role.id})")
        except discord.Forbidden:
            self.logger.info(f"Unable to change the name of a custom role, forbidden (G{ctx.guild.id}/R{role.id})")
            return await ctx.send("I'm unable to edit your custom role.")
        except discord.HTTPException as e:
            self.logger.info(f"Unable to change the name of a custom role (G{ctx.guild.id}/R{role.id}) - {e}")
            return await ctx.send("You gave an invalid name - Discord wouldn't let me change it to your given value.")
        return await ctx.send("Successfully updated your role's name.")

    @customrole.command(cls=utils.Command, aliases=['color'])
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @utils.cooldown.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def colour(self, ctx:utils.Context, *, colour:utils.converters.ColourConverter):
        """
        Change the colour of your custom role.
        """

        # Validate the colour
        # if isinstance(colour, str):
        #     colour_value = utils.converters.ColourConverter.COLOURS_BY_NAME.get(colour)
        #     if colour_value is None:
        #         return await ctx.send("That isn't a valid colour hex code or name.")
        #     colour = discord.Colour(colour_value)

        # Get their role
        role = await self.check_for_custom_role(ctx.author)
        if role is None:
            return await ctx.send(f"You don't have a custom role on this server - set one with `{ctx.prefix}{ctx.command.parent.name} create`.")

        # Edit name
        try:
            await role.edit(color=colour)
            self.logger.info(f"Changed the colour of a custom role to '{colour.value:0>6X}' (G{ctx.guild.id}/R{role.id})")
        except discord.Forbidden:
            self.logger.info(f"Unable to change the colour of a custom role, forbidden (G{ctx.guild.id}/R{role.id})")
            return await ctx.send("I'm unable to edit your custom role.")
        return await ctx.send("Successfully updated your role's colour.")

    @customrole.command(cls=utils.Command)
    @localutils.checks.is_guild_moderator()
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @commands.guild_only()
    async def set(self, ctx:utils.Context, user:discord.Member, *, role:discord.Role):
        """Set a user's custom role to an existing one"""

        # Add it to the database
        async with self.bot.database() as db:
            await db(
                """INSERT INTO custom_roles (guild_id, role_id, user_id)
                VALUES ($1, $2, $3) ON CONFLICT (guild_id, user_id)
                DO UPDATE SET role_id=$2""",
                ctx.guild.id, role.id, user.id
            )
        self.logger.info(f"Set custom role for a user to a current role (G{ctx.guild.id}/R{role.id}/U{user.id})")

        # Add it to the user
        try:
            await user.add_roles(role, reason="Custom role setting")
        except discord.Forbidden:
            pass
        return await ctx.send(f"Set the custom role for {user.mention} to {role.mention}. They can manage it with the `{ctx.prefix}{ctx.command.parent.name} name` and `{ctx.prefix}{ctx.command.parent.name} colour` commands.", allowed_mentions=discord.AllowedMentions(roles=False))

    @customrole.command(cls=utils.Command, aliases=['make'])
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @utils.cooldown.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def create(self, ctx:utils.Context):
        """Create a custom role for the server"""

        # See if they're allowed to make a custom role
        master_role_id = self.bot.guild_settings[ctx.guild.id].get('custom_role_id')
        if master_role_id is None:
            return await ctx.send("This server hasn't set a master role for custom role handling.")
        master_role = ctx.guild.get_role(master_role_id)
        if master_role is None:
            return await ctx.send("The master role for custom role handling on this server is set to a deleted role.")
        if master_role not in ctx.author.roles:
            return await ctx.send(f"You need the `{master_role.name}` role to be able to create a custom role.")

        # Lets trigger some typing babey
        await ctx.trigger_typing()

        # Check they don't already have a role
        current_role = await self.check_for_custom_role(ctx.author)
        if current_role:
            try:
                await current_role.delete()
            except discord.HTTPException:
                pass

        # Create role
        try:
            role_xfix = self.bot.guild_settings[ctx.guild.id].get('custom_role_xfix', None) or '(Custom)'
            if role_xfix.endswith(':'):
                role_name = f"{role_xfix.strip(':')} {ctx.author.name}"
            else:
                role_name = f"{ctx.author.name} {role_xfix.strip(':')}"
            new_role = await ctx.guild.create_role(name=role_name)
            self.logger.info(f"Created custom role in guild (G{ctx.guild.id}/R{new_role.id}/U{ctx.author.id})")
        except discord.Forbidden:
            self.logger.error(f"Couldn't create custom role in guild, forbidden (G{ctx.guild.id}/R{new_role.id}/U{ctx.author.id})")
            return await ctx.send("I'm unable to create new roles on this server.")
        except discord.HTTPException as e:
            self.logger.error(f"Couldn't create custom role in guild (G{ctx.guild.id}/R{new_role.id}/U{ctx.author.id}) - {e}")
            return await ctx.send("Discord wouldn't let me create a new role - maybe this server is at the limit?")

        # Get the right role position
        self.logger.info(f"Sleeping before updating role position... (G{ctx.guild.id})")
        await asyncio.sleep(1)
        position_role_id = self.bot.guild_settings[ctx.guild.id].get('custom_role_position_id')
        position_role = None
        if position_role_id:
            try:
                position_role = [i for i in ctx.guild.roles if i.id == position_role_id][0]
            except IndexError:
                pass

        # Edit the role position
        if position_role:
            try:
                self.logger.info(f"Moving role {new_role.id} to position {position_role.position - 1} (my highest is {new_role.guild.me.top_role.position})")
                await new_role.edit(position_below=position_role, reason="Update positioning")
                self.logger.info(f"Edited custom role position in guild (G{ctx.guild.id}/R{new_role.id})")
            except discord.Forbidden:
                self.logger.error(f"Couldn't move custom role, forbidden (G{ctx.guild.id}/U{ctx.author.id})")
            except discord.HTTPException as e:
                self.logger.error(f"Couldn't move custom role role (G{ctx.guild.id}/U{ctx.author.id}) - {e}")

        # Add it to the database
        async with self.bot.database() as db:
            await db(
                """INSERT INTO custom_roles (guild_id, role_id, user_id)
                VALUES ($1, $2, $3) ON CONFLICT (guild_id, user_id)
                DO UPDATE SET role_id=$2""",
                ctx.guild.id, new_role.id, ctx.author.id
            )

        # Add it to the user
        try:
            await ctx.author.add_roles(new_role, reason="Custom role creation")
        except discord.Forbidden:
            return await ctx.send(f"I created the custom role ({new_role.mention}) but I was unable to add it to you.")
        return await ctx.send(f"Created your custom role - {new_role.mention}. You can manage it with the `{ctx.prefix}{ctx.command.parent.name} name` and `{ctx.prefix}{ctx.command.parent.name} colour` commands. You may need to ask a moderator to move it for you, so your colour displays properly.")


def setup(bot:utils.Bot):
    x = CustomRoleHandler(bot)
    bot.add_cog(x)

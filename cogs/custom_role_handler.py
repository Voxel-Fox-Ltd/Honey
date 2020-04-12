import typing

import discord
from discord.ext import commands

from cogs import utils


class CustomRoleHandler(utils.Cog):

    @commands.group(cls=utils.Group)
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def customrole(self, ctx:utils.Context):
        """The parent command to manage your custom role"""

        # See if we invoke a real command
        if ctx.invoked_subcommand is not None:
            return

        # Throw em some help
        return await ctx.send(f"This command is used so you can manage your custom role on this server, should you have one. See `{ctx.prefix}help {ctx.invoked_with}` to learn more.")

    async def check_for_custom_role(self, ctx:utils.Context) -> typing.Optional[discord.Role]:
        """Returns the user's custom role object for the server, or None if they
        don't have one. This does NOT check for whether they can/cannot have one"""

        async with self.bot.database() as db:
            rows = await db("SELECT * FROM custom_roles WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, ctx.author.id)
        if not rows:
            return None
        return ctx.guild.get_role(rows[0]['role_id'])

    @customrole.command(cls=utils.Command)
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @utils.cooldown.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def name(self, ctx:utils.Context, *, name:commands.clean_content):
        """Change the name of your custom role"""

        # Get their role
        role = await self.check_for_custom_role(ctx)
        if role is None:
            return await ctx.send(f"You don't have a custom role on this server - set one with `{ctx.prefix}{ctx.command.parent.name} create`.")

        # Edit name
        try:
            await role.edit(name=name)
        except discord.Forbidden:
            return await ctx.send("I'm unable to edit your custom role.")
        except discord.NotFound:
            pass
        except discord.HTTPException:
            return await ctx.send("You gave an invalid name - Discord wouldn't let me change it to your given value.")
        return await ctx.send("Successfully updated your role's name.")

    @customrole.command(cls=utils.Command, aliases=['color'])
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @utils.cooldown.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def colour(self, ctx:utils.Context, *, colour:discord.Colour):
        """Change the colour of your custom role"""

        # Get their role
        role = await self.check_for_custom_role(ctx)
        if role is None:
            return await ctx.send(f"You don't have a custom role on this server - set one with `{ctx.prefix}{ctx.command.parent.name} create`.")

        # Edit name
        try:
            await role.edit(color=colour)
        except discord.Forbidden:
            return await ctx.send("I'm unable to edit your custom role.")
        except discord.NotFound:
            pass
        return await ctx.send("Successfully updated your role's colour.")

    # @customrole.command(cls=utils.Command)
    # @utils.checks.is_guild_moderator()
    # @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    # @commands.guild_only()
    # async def set(self, ctx:utils.Context, user:discord.Member, *, role:discord.Role):
    #     """Set a user's custom role to an existing one"""

    #     # Add it to the database
    #     async with self.bot.database() as db:
    #         await db(
    #             """INSERT INTO custom_roles (guild_id, role_id, user_id)
    #             VALUES ($1, $2, $3) ON CONFLICT (guild_id, user_id)
    #             DO UPDATE SET role_id=$2""",
    #             ctx.guild.id, role.id, user.id
    #         )

    #     # Add it to the user
    #     try:
    #         await user.add_roles(role, reason="Custom role setting")
    #     except discord.Forbidden:
    #         return await ctx.send(f"I was unable to add the role to {user.mention}.")
    #     return await ctx.send(f"Set the custom role for {user.mention} to {role.mention}. They can manage it with the `{ctx.prefix}{ctx.command.parent.name} name` and `{ctx.prefix}{ctx.command.parent.name} colour` commands.")

    @customrole.command(cls=utils.Command, aliases=['make'])
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    @utils.cooldown.cooldown(1, 60 * 10, commands.BucketType.member)
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
        current_role = await self.check_for_custom_role(ctx)
        if current_role:
            try:
                await current_role.delete()
            except discord.HTTPException:
                pass

        # See if the server has a position set
        position = 1
        position_role_id = self.bot.guild_settings[ctx.guild.id].get('custom_role_position_id')
        if position_role_id:
            position_role = ctx.guild.get_role(position_role_id)
            if position_role:
                position = position_role.position

        # Create role
        try:
            new_role = await ctx.guild.create_role(name=f"Custom Role: {ctx.author.id}")
            await new_role.edit(position=position)
        except discord.Forbidden:
            return await ctx.send("I'm unable to create new roles on this server.")
        except discord.HTTPException:
            return await ctx.send("Discord wouldn't let me create a new role - maybe this server is at the limit?")

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

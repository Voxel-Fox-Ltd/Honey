from datetime import datetime as dt

import discord
from discord.ext import tasks

from cogs import utils


class TemporaryRoleHandler(utils.Cog):

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.role_handler.start()

    def cog_unload(self):
        self.role_handler.stop()

    @tasks.loop(minutes=1)
    async def role_handler(self):
        """Loops once a minute to remove the roles of a user should they need to be taken"""

        # Get data
        async with self.bot.database() as db:
            temporary_roles_rows = await db("SELECT * FROM temporary_roles")
        if not temporary_roles_rows:
            return

        # Remove roles
        removed_roles = []
        for row in temporary_roles_rows:
            if row['remove_timestamp'] > dt.utcnow():
                continue

            # Get the relevant information
            removed_roles.append((row['guild_id'], row['role_id'], row['user_id']))
            guild = self.bot.get_guild(row['guild_id'])
            member = guild.get_member(row['user_id'])
            role = guild.get_role(row['role_id'])

            # Remove the role
            if role is not None and row['delete_role']:
                try:
                    await role.delete(reason="Temporary role expired")
                    self.logger.info(f"Deleted role - duration expired (G{guild.id}/R{role.id})")
                except (discord.Forbidden, discord.NotFound) as e:
                    self.logger.info(f"Couldn't delete duration expired role (G{guild.id}/R{role.id}) - {e}")
            elif role is not None and member is not None:
                try:
                    await member.remove_roles(role, reason="Role duration expired")
                    self.logger.info(f"Removed role from user - duration expired (G{guild.id}/R{role.id}/U{member.id})")
                except (discord.Forbidden, discord.NotFound) as e:
                    self.logger.info(f"Couldn't remove duration expired role form user (G{guild.id}/R{role.id}/U{member.id}) - {e}")

            # DM the user
            if role is not None and member is not None and row['dm_user']:
                try:
                    await member.send(f"Removed the `{role.name}` role from you in the server **{guild.name}** - duration expired.")
                    self.logger.info(f"Sent DM to user about expired role (G{guild.id}/R{role.id}/U{member.id})")
                except (discord.Forbidden, discord.NotFound):
                    self.logger.info(f"Couldn't send DM to user about expired role (G{guild.id}/R{role.id}/U{member.id})")

        # Remove from db
        async with self.bot.database() as db:
            for guild_id, role_id, user_id in removed_roles:
                await db("DELETE FROM temporary_roles WHERE guild_id=$1 AND role_id=$2 AND user_id=$3", guild_id, role_id, user_id)

        # Disconnect from db
        self.logger.info(f"Removed/deleted {len(removed_roles)} expired temporary roles")

    @role_handler.before_loop
    async def before_role_handler(self):
        await self.bot.wait_until_ready()


def setup(bot:utils.Bot):
    x = TemporaryRoleHandler(bot)
    bot.add_cog(x)

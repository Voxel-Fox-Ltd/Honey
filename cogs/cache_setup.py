import voxelbotutils as vbu


class CacheSetup(vbu.Cog):

    async def cache_setup(self, db):
        """
        Wowowowow Honey has a lot of things in its database that I want to cache so here we go motherfuckers
        """

        # Get stored interaction cooldowns
        data = await self.bot._get_list_table_data(db, 'role_list', 'Interactions')
        for row in data:
            self.bot.guild_settings[row['guild_id']].setdefault('role_interaction_cooldowns', dict())[row['role_id']] = int(float(row['value']))

        # Get max sona count
        data = await self.bot._get_list_table_data(db, 'role_list', 'SonaCount')
        for row in data:
            self.bot.guild_settings[row['guild_id']].setdefault('role_sona_count', dict())[row['role_id']] = int(row['value'])

        # Get buyable roles
        data = await self.bot._get_list_table_data(db, 'role_list', 'BuyableRoles')
        for row in data:
            self.bot.guild_settings[row['guild_id']].setdefault('buyable_roles', dict())[row['role_id']] = int(row['value'])

        # Get buyable temp roles
        data = await self.bot._get_all_table_data(db, 'buyable_temporary_roles')
        for row in data:
            self.bot.guild_settings[row['guild_id']].setdefault('buyable_temporary_roles', dict())[row['role_id']] = {
                "price": row['price'],
                "duration": row['duration'],
            }

        # Get roles to be removed on mute
        data = await self.bot._get_list_table_data(db, 'role_list', 'RemoveOnMute')
        for row in data:
            self.bot.guild_settings[row['guild_id']].setdefault('removed_on_mute_roles', list()).append(row['role_id'])

        # Get disabled sona channels
        data = await self.bot._get_list_table_data(db, 'channel_list', 'DisabledSonaChannel')
        for row in data:
            self.bot.guild_settings[row['guild_id']].setdefault('disabled_sona_channels', list()).append(row['channel_id'])

        # Get disabled interaction channels
        data = await self.bot._get_list_table_data(db, 'channel_list', 'DisabledInteractionChannel')
        for row in data:
            self.bot.guild_settings[row['guild_id']].setdefault('disabled_interaction_channels', list()).append(row['channel_id'])


def setup(bot: vbu.Bot):
    x = CacheSetup(bot)
    bot.add_cog(x)

import discord
from discord.ext import commands

from cogs import utils


class ShopHandler(utils.Cog):

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
            embed.add_field(
                "Paint (\N{LOWER LEFT PAINTBRUSH})",
                f"Paint your friends, paint your enemies. Adds a custom paint colour role to you for an hour.\n**Costs 100 {coin_emoji}**",
                inline=False,
            )
        shop_message = await shop_channel.send(embed=embed)
        await shop_message.add_reaction("\N{LOWER LEFT PAINTBRUSH}")

        # Save it all to db
        async with self.bot.database() as db:
            await db(
                """INSERT INTO shopping_channels (guild_id, channel_id, message_id) VALUES ($1, $2, $3)
                ON CONFLICT (guild_id) DO UPDATE SET channel_id=excluded.channel_id, message_id=excluded.message_id""",
                ctx.guild.id, shop_channel.id, shop_message.id
            )

        # And tell the mod it's done
        await ctx.send(f"Created new shop channel at {shop_channel.mention} - please verify the channel works before updating permissions for the everyone role.")


def setup(bot:utils.Bot):
    x = ShopHandler(bot)
    bot.add_cog(x)

import discord
from discord.ext import commands

from cogs import utils


class ItemHandler(utils.Cog):

    @commands.command(cls=utils.Command, aliases=['inv', 'inventory'])
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
                item_data = [i for i in self.bot.get_cog("ShopHandler").SHOP_ITEMS.values() if i[1] == row['item_name']][0]
                inventory_string_rows.append(f"{row['amount']}x {item_data[0] or item_data[1]}")
            embed.description = f"**{coin_rows[0]['amount']:,} {coin_emoji}**\n" + "\n".join(inventory_string_rows)
        return await ctx.send(embed=embed)


def setup(bot:utils.Bot):
    x = ItemHandler(bot)
    bot.add_cog(x)

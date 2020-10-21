import random

from datetime import datetime as dt

import discord
from discord.ext import commands
from discord.ext import tasks
import voxelbotutils as utils


class GiveawayHandler(utils.Cog):

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.giveaway_expiry_handler.start()

    def cog_unload(self):
        self.giveaway_expiry_handler.stop()

    @commands.command(cls=utils.Command)
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, add_reactions=True)
    async def giveaway(self, ctx:utils.Context, duration:utils.TimeValue, winner_count:int, *, giveaway_name:str):
        """
        Start a giveaway.
        """

        # Validate winner count
        if winner_count < 1:
            return await ctx.send("You need to give a winner count larger than 0.")
        if winner_count > 200:
            return await ctx.send("You can't give more than 200 winners.")

        # Create the embed
        with utils.Embed(colour=0x00ff00) as embed:
            embed.title = giveaway_name
            embed.description = "Click the reaction below to enter!"
            embed.set_footer(text=f"{winner_count} winner{'s' if winner_count > 1 else ''} | Ends at")
            embed.timestamp = dt.utcnow() + duration.delta
        giveaway_message = await ctx.send(embed=embed)

        # Add to database
        async with self.bot.database() as db:
            await db(
                """INSERT INTO giveaways (channel_id, message_id, winner_count, ending_time, description)
                VALUES ($1, $2, $3, $4, $5)""",
                giveaway_message.channel.id, giveaway_message.id, winner_count, dt.utcnow() + duration.delta, giveaway_name,
            )

        # Add reaction
        await giveaway_message.add_reaction("\N{PARTY POPPER}")

    @tasks.loop(seconds=30)
    async def giveaway_expiry_handler(self):
        """
        Handles giveaways expiring.
        """

        # Grab expired stuff from the database
        db = await self.bot.database.get_connection()
        rows = await db("SELECT * FROM giveaways WHERE ending_time < TIMEZONE('UTC', NOW())")
        if not rows:
            await db.disconnect()
            return

        # Go and expire the giveaways
        expired_giveaways = []
        for giveaway in rows:

            # Get the message
            channel = self.bot.get_channel(giveaway['channel_id'])
            try:
                message = await channel.fetch_message(giveaway['message_id'])
            except (discord.NotFound, AttributeError):
                self.logger.info(f"No giveaway with message ID {giveaway['message_id']} could be found")
                expired_giveaways.append(giveaway['message_id'])
                continue

            # Edit the message
            try:
                embed = message.embeds[0]
                embed.colour = 0xff0000
                await message.edit(embed=embed)
            except Exception:
                pass

            # Get the reacted users
            try:
                reaction = [i for i in message.reactions if str(i.emoji) == "\N{PARTY POPPER}"][0]
            except IndexError:
                self.logger.info(f"Giveaway with message ID {giveaway['message_id']} had no valid reactions")
                expired_giveaways.append(message.id)
                continue
            all_users = await reaction.users().flatten()
            reacted_users = [i for i in all_users if not i.bot and channel.guild.get_member(i.id) is not None]

            # See who should have won
            winners = []
            while len(winners) < giveaway['winner_count'] and len(reacted_users) > 0:
                new_winner = random.choice(reacted_users)
                winners.append(new_winner)
                reacted_users.remove(new_winner)

            # Send winner message
            text, old_text = f"Winner{'s' if len(winners) > 1 else ''} of the giveaway **{giveaway['description']}**: ", ""
            last_winner = None
            while len(winners) > 0:
                last_winner = winners[0]
                text += f"{last_winner.mention}, "
                if len(text.strip(' ,')) > 2000:
                    await channel.send(old_text.strip(' ,'))
                    text = f"{last_winner.mention}, "
                old_text = text[:]
                winners.remove(last_winner)
            if len(text.strip(' ,')) > 2000:
                await channel.send(old_text.strip(' ,'))
                await channel.send(last_winner.mention)
            else:
                await channel.send(text.strip(' ,'))
            self.logger.info(f"Sent expired giveaway message (G{message.guild.id}/C{message.channel.id}/M{message.id})")
            expired_giveaways.append(giveaway['message_id'])

        # Remove expired giveaways from the database
        await db("DELETE FROM giveaways WHERE message_id=ANY($1::BIGINT[])", expired_giveaways)
        await db.disconnect()

    @giveaway_expiry_handler.before_loop
    async def before_giveaway_expiry_handler(self):
        await self.bot.wait_until_ready()


def setup(bot:utils.Bot):
    x = GiveawayHandler(bot)
    bot.add_cog(x)

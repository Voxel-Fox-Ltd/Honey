import asyncio

import discord
from discord.ext import commands

from cogs import utils


class SuggestionHandler(utils.Cog):

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        pass

    @commands.command(cls=utils.Command, aliases=['suggestion', 'suggestions'])
    @commands.bot_has_permissions(send_messages=True)
    async def suggest(self, ctx:utils.Context, *, suggestion:str):
        """Send in a suggestion to the server"""

        if not suggestion:
            raise utils.errors.MissingRequiredArgumentString("suggestion")

        # Ask where the suggestion is for
        user = ctx.author
        try:
            m = await user.send("Is this a _bot_ suggestion (0\N{COMBINING ENCLOSING KEYCAP}) or a _server_ suggestion (1\N{COMBINING ENCLOSING KEYCAP})?")
        except discord.Forbidden:
            return await ctx.send("I couldn't send you a DM.")
        await ctx.send("Sent you a DM!")
        await m.add_reaction("0\N{COMBINING ENCLOSING KEYCAP}")
        await m.add_reaction("1\N{COMBINING ENCLOSING KEYCAP}")

        # See what they're talkin about
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == m.id and u.id == user.id, timeout=120)
        except asyncio.TimeoutError:
            return await user.send("Timed out asking about your suggestion.")

        # Generate the embed
        with utils.Embed(use_random_colour=True) as embed:
            embed.description = suggestion
            if ctx.message.attachments:
                embed.add_field("Attachments", ", ".join([i.url for i in ctx.message.attachments]))
            embed.set_author_to_user(ctx.author)
            embed.timestamp = ctx.message.created_at
            embed.set_footer(f"User ID {ctx.author.id}")

        # See how they reacted - assume it's a server suggestion if it was an invalid emoji
        if str(reaction.emoji) == "0\N{COMBINING ENCLOSING KEYCAP}":
            suggestion_channel_id = self.bot.config['channels']['suggestion_channel']
            suggestion_channel = self.bot.get_channel(suggestion_channel_id)
            try:
                await suggestion_channel.send(embed=embed)
            except (discord.HTTPException, AttributeError) as e:
                return await user.send(f"Your suggestion could not be sent in to the development team - {e}")
            return await user.send("Your suggestion has been successfully sent in to the bot development team.")

        # Send the suggestion to the server
        if ctx.guild is None:
            return await user.send("You can't run this command in DMs if you're trying to make a server suggestion.")
        suggestion_channel_id = self.bot.guild_settings[ctx.guild.id]['suggestion_channel_id']
        if not suggestion_channel_id:
            return await user.send(f"**{ctx.guild.name}** hasn't set up a suggestion channel for me to send suggestions to.")
        suggestion_channel = self.bot.get_channel(suggestion_channel_id)
        if not suggestion_channel:
            return await user.send(f"**{ctx.guild.name}** has set up an invalid suggestion channel for me to send suggestions to.")
        try:
            embed.set_footer("Send in a suggestion with the 'suggest' command")
            await suggestion_channel.send(embed=embed)
        except (discord.HTTPException, AttributeError) as e:
            return await user.send(f"I couldn't send in your suggestion into {suggestion_channel.mention} - {e}")
        return await user.send("Your suggestion has been successfully sent in to the server's suggestions channel.")


def setup(bot:utils.Bot):
    x = SuggestionHandler(bot)
    bot.add_cog(x)

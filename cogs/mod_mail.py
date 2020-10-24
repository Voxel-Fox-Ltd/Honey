import discord

from cogs import utils


class ModMail(utils.Cog):

    @utils.Cog.listener("on_message")
    async def modmail_handler(self, message):

        if not isinstance(message.channel, discord.DMChannel):
            return

        ctx = await self.bot.get_context(message, cls=utils.Context)
        if ctx.command is not None or ctx.author.bot is True:
            return

        # Get all guilds that the user shares with the bot and get which ones have modmail enabled
        guilds = [g for g in self.bot.guilds if ctx.author in g.members]
        guilds_with_modmail = [guild for guild in guilds if self.bot.guild_settings[guild.id]["enable_modmail"] is True]

        # if there a more then 1 guild lets ask the user for the guild they want
        if len(guilds_with_modmail) > 1:

            # Lets make a list of dicts of info that'll be needed later
            enumerated_guilds = [{
                "index": index,
                "emoji": f"{index}\N{variation selector-16}\N{combining enclosing keycap}",
                "guild": guild,
            } for index, guild in enumerate(guilds_with_modmail)]

            # Create and send selector page and add reactions
            with utils.Embed() as e:
                e.title = "Select what guild to send message to?"
                decription_text = []
                for x in enumerated_guilds:
                    text = f"{x['emoji']} - {x['guild'].name}"
                    decription_text.append(text)
                e.description = "\n".join(decription_text)
            sent_message = await ctx.send(embed=e)
            for guild in enumerated_guilds:
                await sent_message.add_reaction(guild["emoji"])

            # Now we wait for a response from user
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=lambda r, u: u is message.author)

            # woo we finally have the guild the user wants
            guild = [x['guild'] for x in enumerated_guilds if reaction.emoji in x.values()][0]

        # There's only one guild so that makes it easy
        elif len(guilds_with_modmail) == 1:
            guild = guilds_with_modmail[0]

        # Shouldn't have to call this but just incase
        else:
            return


def setup(bot: utils.Bot):
    x = ModMail(bot)
    bot.add_cog(x)
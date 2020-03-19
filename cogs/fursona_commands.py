import asyncio
import re
import typing

import discord
from discord.ext import commands

from cogs import utils


class FursonaComamnds(utils.Cog):

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.currently_setting_sonas = set()

    async def send_verification_message(self, user:discord.User, message:str, timeout:float=600, check:callable=None) -> discord.Message:
        """Sends a verification message to a user, waits for a response, and returns that message"""

        # Send message
        try:
            await user.send(message)
        except discord.Forbidden:
            self.logger.info(f"DMs of {user.id} are closed.")
            return None

        # Set default check
        if check is None:
            check = lambda m: isinstance(m.channel, discord.DMChannel) and m.author.id == user.id and m.content

        # Wait for response
        try:
            return await self.bot.wait_for(
                "message",
                check=check,
                timeout=timeout
            )
        except asyncio.TimeoutError:
            try:
                await user.send("You waited too long to respond to this message - try again later.")
            except discord.Forbidden:
                pass
            return None

    @classmethod
    def get_image_from_message(cls, message:discord.Message) -> typing.Optional[str]:
        """Gets an image url from a given message"""

        if cls.is_image_url(message.content):
            return message.content
        if message.attachments and cls.is_image_url(message.attachments[0].url):
            return message.attachments[0].url
        return None

    @staticmethod
    def is_image_url(content:str) -> bool:
        """Returns whether a given string is a valid image url"""

        return re.search(r"^(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png|jpeg)$", content, re.IGNORECASE)

    @commands.command(cls=utils.Command)
    @commands.check(utils.checks.is_verified)
    @commands.guild_only()
    async def setsona(self, ctx:utils.Context):
        """Stores your fursona information in the bot"""

        # See if the user already has a fursona stored
        async with self.bot.databse() as db:
            rows = await db("SELECT * FROM fursonas WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, ctx.author.id)
        if rows:
            return await ctx.send("You already have a fursona set!")

        # See if they're setting one up already
        if ctx.author.id in self.currently_setting_sonas:
            return await ctx.send("You're already setting up a sona! Please finish that one off first!")

        # Try and send them an initial DM
        user = ctx.author
        try:
            await user.send(f"Now talking you through setting up your sona on **{ctx.guild.name}**!")
        except discord.Forbidden:
            return await ctx.send("I couldn't send you a DM! Please open your DMs for this server and try again.")
        self.currently_setting_sonas.add(user.id)
        await ctx.send("Sent you a DM!")

        # Now we wanna ask them each thing wow so fun
        name_message = await self.send_verification_message(user, "What is the name of your sona?")
        if name_message is None:
            return
        gender_message = await self.send_verification_message(user, "What's your sona's gender?")
        if gender_message is None:
            return
        age_message = await self.send_verification_message(user, "How old is your sona?")
        if age_message is None:
            return
        species_message = await self.send_verification_message(user, "What species is your sona?")
        if species_message is None:
            return
        orientation_message = await self.send_verification_message(user, "What's your sona's orientation?")
        if orientation_message is None:
            return
        height_message = await self.send_verification_message(user, "How tall is your sona?")
        if height_message is None:
            return
        weight_message = await self.send_verification_message(user, "What's the weight of your sona?")
        if weight_message is None:
            return
        bio_message = await self.send_verification_message(user, "What's the bio of your sona?")
        if bio_message is None:
            return

        def check(m) -> bool:
            return all([
                isinstance(m.channel, discord.DMChannel),
                m.author.id == user.id,
                any([
                    m.content.lower() == "no",
                    self.get_image_from_message(m)
                ]),
            ])
        image_message = await self.send_verification_message(user, "Do you have an image for your sona? Please post it if you have one (as a link or an attachment), or say `no` to continue without.", check=check)
        if image_message is None:
            return
        check = lambda m: isinstance(m.channel, discord.DMChannel) and m.author.id == user.id and m.content.lower() in ["yes", "no"]
        nsfw_message = await self.send_verification_message(user, "Is your sona NSFW? Please either say `yes` or `no`.", check=check)
        if nsfw_message is None:
            return

        # Format that into data
        image_content = None if image_message.content.lower() == "no" else self.get_image_from_message(image_message)
        information = {
            'guild_id': ctx.guild.id,
            'user_id': user.id,
            'index': 0,
            'name': name_message.content,
            'gender': gender_message.content,
            'age': age_message.content,
            'species': species_message.content,
            'orientation': orientation_message.content,
            'height': height_message.content,
            'weight': weight_message.content,
            'bio': bio_message.content,
            'image': image_content,
            'nsfw': nsfw_message.content == "yes",
        }
        sona_object = utils.Fursona(**information)

        # Send it back to the user so we can make sure it sends
        try:
            await user.send(embed=sona_object.get_embed())
        except discord.HTTPException as e:
            return await user.send(f"I couldn't send that embed to you - `{e}`. Please try again later.")

        # Send it to the verification channel
        guild_settings = self.bot.guild_settings.get(ctx.guild.id)
        modmail_channel_id = guild_settings.get("fursona_modmail_channel_id")
        if modmail_channel_id:
            modmail_channel = self.bot.get_channel(modmail_channel_id)
            if modmail_channel is None:
                return await user.send(f"The moderators for the server **{ctx.guild.name}** have set their fursona modmail channel to an invalid ID - please inform them of such and try again later.")
            try:
                modmail_message = await modmail_channel.send(f"New sona submission from {user.mention}", embed=sona_object.get_embed())
            except discord.Forbidden:
                return await user.send(f"The moderators for the server **{ctx.guild.name}** have disallowed me from sending messages to their fursona modmail channel - please inform them of such and try again later.")
            try:
                modmail_message.add_reaction("\N{HEAVY CHECK MARK}")
                modmail_message.add_reaction("\N{HEAVY MULTIPLICATION X}")
                modmail_message.add_reaction("\N{SMILING FACE WITH HORNS}")
            except discord.Forbidden:
                await modmail_message.delete()
                return await user.send(f"The moderators for the server **{ctx.guild.name}** have disallowed me from adding reactions in their fursona modmail channel - please inform them of such and try again later.")

        # Save sona to database now it's sent properly
        async with self.bot.database() as db:
            await sona_object.save(db)

        # Tell them everything was done properly
        if modmail_channel_id:
            return await user.send("Your fursona has been sent to the moderators for approval! Please be patient as they review.")
        return await user.send("Your fursona has been saved!")

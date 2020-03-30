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
        async with self.bot.database() as db:
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
            return self.currently_setting_sonas.remove(user.id)
        gender_message = await self.send_verification_message(user, "What's your sona's gender?")
        if gender_message is None:
            return self.currently_setting_sonas.remove(user.id)
        age_message = await self.send_verification_message(user, "How old is your sona?")
        if age_message is None:
            return self.currently_setting_sonas.remove(user.id)
        species_message = await self.send_verification_message(user, "What species is your sona?")
        if species_message is None:
            return self.currently_setting_sonas.remove(user.id)
        orientation_message = await self.send_verification_message(user, "What's your sona's orientation?")
        if orientation_message is None:
            return self.currently_setting_sonas.remove(user.id)
        height_message = await self.send_verification_message(user, "How tall is your sona?")
        if height_message is None:
            return self.currently_setting_sonas.remove(user.id)
        weight_message = await self.send_verification_message(user, "What's the weight of your sona?")
        if weight_message is None:
            return self.currently_setting_sonas.remove(user.id)
        bio_message = await self.send_verification_message(user, "What's the bio of your sona?")
        if bio_message is None:
            return self.currently_setting_sonas.remove(user.id)

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
            return self.currently_setting_sonas.remove(user.id)
        check = lambda m: isinstance(m.channel, discord.DMChannel) and m.author.id == user.id and m.content.lower() in ["yes", "no"]
        nsfw_message = await self.send_verification_message(user, "Is your sona NSFW? Please either say `yes` or `no`.", check=check)
        if nsfw_message is None:
            return self.currently_setting_sonas.remove(user.id)

        # Format that into data
        image_content = None if image_message.content.lower() == "no" else self.get_image_from_message(image_message)
        information = {
            'guild_id': ctx.guild.id,
            'user_id': user.id,
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
            self.currently_setting_sonas.remove(user.id)
            return await user.send(f"I couldn't send that embed to you - `{e}`. Please try again later.")

        # Send it to the verification channel
        guild_settings = self.bot.guild_settings[ctx.guild.id]
        modmail_channel_id = guild_settings.get("fursona_modmail_channel_id")
        if modmail_channel_id:
            modmail_channel = self.bot.get_channel(modmail_channel_id)
            if modmail_channel is None:
                self.currently_setting_sonas.remove(user.id)
                return await user.send(f"The moderators for the server **{ctx.guild.name}** have set their fursona modmail channel to an invalid ID - please inform them of such and try again later.")
            try:
                modmail_message = await modmail_channel.send(f"New sona submission from {user.mention}", embed=sona_object.get_embed())
            except discord.Forbidden:
                self.currently_setting_sonas.remove(user.id)
                return await user.send(f"The moderators for the server **{ctx.guild.name}** have disallowed me from sending messages to their fursona modmail channel - please inform them of such and try again later.")
            try:
                await modmail_message.add_reaction("\N{HEAVY CHECK MARK}")
                await modmail_message.add_reaction("\N{HEAVY MULTIPLICATION X}")
                await modmail_message.add_reaction("\N{SMILING FACE WITH HORNS}")
            except discord.Forbidden:
                await modmail_message.delete()
                self.currently_setting_sonas.remove(user.id)
                return await user.send(f"The moderators for the server **{ctx.guild.name}** have disallowed me from adding reactions in their fursona modmail channel - please inform them of such and try again later.")

        # Save sona to database now it's sent properly
        async with self.bot.database() as db:
            await sona_object.save(db)

        # Tell them everything was done properly
        self.currently_setting_sonas.remove(user.id)
        if modmail_channel_id:
            return await user.send("Your fursona has been sent to the moderators for approval! Please be patient as they review.")
        return await user.send("Your fursona has been saved!")

    @utils.Cog.listener("on_raw_reaction_add")
    async def fursona_verification_reaction_handler(self, payload:discord.RawReactionActionEvent):
        """Listens for reactions being added to fursona approval messages"""

        # Check not a bot
        if self.bot.get_user(payload.user_id).bot:
            return

        # Check if we're in a modmail channel
        guild_settings = self.bot.guild_settings[payload.guild_id]
        modmail_channel_id = guild_settings.get("fursona_modmail_channel_id")
        if payload.channel_id != modmail_channel_id:
            return

        # Get the message
        self.logger.info(f"Dealing with sona modmail on guild {payload.guild_id} with message {payload.message_id}")
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        fursona_embed = message.embeds[0]
        fursona_user_id = int(fursona_embed.footer.text.split(' ')[2])
        fursona_name = fursona_embed.title
        fursona_member = self.bot.get_guild(payload.guild_id).get_member(fursona_user_id)
        if fursona_member is None:
            self.logger.info(f"No member could be found - message {payload.message_id}")
            return

        # See the mod's reaction
        emoji = str(payload.emoji)
        verified = False
        nsfw = False
        archive_channel_id = None
        if emoji == "\N{HEAVY MULTIPLICATION X}":
            pass
        elif emoji == "\N{HEAVY CHECK MARK}":
            archive_channel_id = guild_settings.get("fursona_accept_archive_channel_id")
            verified = True
            nsfw = fursona_embed.footer.text.split(' ')[4] == 'NSFW'
        elif emoji == "\N{SMILING FACE WITH HORNS}":
            archive_channel_id = guild_settings.get("fursona_accept_nsfw_archive_channel_id")
            verified = True
            nsfw = True
        else:
            self.logger.info(f"Invalid reaction in sona modmail on guild {payload.guild_id} with message {payload.message_id}")
            return  # Invalid reaction, just ignore

        # Update the information
        async with self.bot.database() as db:
            if verified is False:
                await db("DELETE FROM fursonas WHERE guild_id=$1 AND user_id=$2 AND name=$3", payload.guild_id, fursona_member.id, fursona_name)
            else:
                await db("UPDATE fursonas SET verified=true, nsfw=$4 WHERE guild_id=$1 AND user_id=$2 AND name=$3", payload.guild_id, fursona_member.id, fursona_name, nsfw)

        # Post it to the archive
        if archive_channel_id:
            try:
                archive_channel = self.bot.get_channel(archive_channel_id)
                await archive_channel.send(embed=fursona_embed)
            except discord.Forbidden:
                pass

        # Delete from modmail
        try:
            await message.delete()
        except discord.NotFound:
            pass

        # Tell the user about it
        try:
            if verified:
                await fursona_member.send(f"Your fursona, `{fursona_name}`, on **{fursona_member.guild.name}** has been accepted!")
            else:
                await fursona_member.send(f"Your fursona, `{fursona_name}`, on **{fursona_member.guild.name}** has been declined.")
        except discord.Forbidden:
            pass

    @commands.command(cls=utils.Command, aliases=['getsona'])
    @commands.guild_only()
    async def sona(self, ctx:utils.Context, user:typing.Optional[discord.Member], *, name:str=None):
        """Gets your sona"""

        # Get the sonas
        user = user or ctx.author
        async with self.bot.database() as db:
            if name is None:
                rows = await db("SELECT * FROM fursonas WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, user.id)
            else:
                rows = await db("SELECT * FROM fursonas WHERE guild_id=$1 AND user_id=$2 AND LOWER(name)=LOWER($3)", ctx.guild.id, user.id, name)

        # Check if they have a valid sona
        if not rows:
            return await ctx.send(f"{user.mention} has no sona set up on this server.")
        elif len(rows) > 1:
            available_sonas = [i['name'] for i in rows]
            available_string = ', '.join(f"`{name}`" for name in available_sonas)
            return await ctx.send(f"{user.mention} has more than one sona set - please get their sona using its name. Available sonas: {available_string}")
        if rows[0]['verified'] is False:
            return await ctx.send(f"{user.mention}'s sona has not yet been verified.")

        # Wew it's sona time let's go
        sona = utils.Fursona(**rows[0])
        return await ctx.send(embed=sona.get_embed(mention_user=True))

    @commands.command(cls=utils.Command, ignore_extra=False)
    @commands.guild_only()
    async def deletesona(self, ctx:utils.Context, *, name:str=None):
        """Deletes your sona"""

        db = await self.bot.database.get_connection()

        # See if they have a sona already
        if name is None:
            rows = await db("SELECT * FROM fursonas WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, ctx.author.id)
        else:
            rows = await db("SELECT * FROM fursonas WHERE guild_id=$1 AND user_id=$2 AND LOWER(name)=LOWER($3)", ctx.guild.id, ctx.author.id, name)
        if not rows:
            await db.disconnect()
            return await ctx.send("You have no sona set for you to delete.")
        elif len(rows) > 1:
            await db.disconnect()
            available_sonas = [i['name'] for i in rows]
            available_string = ', '.join(f"`{name}`" for name in available_sonas)
            return await ctx.send(f"You have multiple sonas - please specify which you want to delete. Available sonas: {available_string}")

        # Delete it from pending
        if rows[0]['verified'] is False:
            modmail_channel_id = self.bot.guild_settings[ctx.guild.id].get('fursona_modmail_channel_id')
            if modmail_channel_id is not None:
                modmail_channel = self.bot.get_channel(modmail_channel_id)
                if modmail_channel is not None:
                    found_message = None
                    async for message in modmail_channel.history():
                        if message.author.id == self.bot.user.id and message.embeds and message.embeds[0].footer.text.split(' ') == str(ctx.author.id):
                            found_message = message
                            break
                    try:
                        await found_message.delete()
                    except (discord.Forbidden, AttributeError):
                        pass

        # Delete it from db
        await db("DELETE FROM fursonas WHERE guild_id=$1 AND user_id=$2 AND LOWER(name)=LOWER($3)", ctx.guild.id, ctx.author.id, name)
        await db.disconnect()
        return await ctx.send("Deleted your sona.")


def setup(bot:utils.Bot):
    x = FursonaComamnds(bot)
    bot.add_cog(x)

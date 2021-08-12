import asyncio
import re
import typing
import json

import discord
from discord.ext import commands
import asyncpg
import voxelbotutils as vbu

from cogs import utils


class FursonaCommands(vbu.Cog):

    OTHER_FURRY_GUILD_DATA = [
        {
            "name": "The Furry Kingdom",
            "guild_id": 587434387079954502,
            "url": "http://51.15.228.168:8080/api/v1/sona",
            "params": {
                "user_id": "{user.id}"
            },
            "headers": {
            },
        },
        {
            "name": "Winterhaven",
            "guild_id": 676902163468910615,
            "url": "http://winterhaven.voxelfox.co.uk/api/v1/sona",
            "params": {
                "user_id": "{user.id}"
            },
            "headers": {
            },
        },
    ]

    CHECK_MARK_EMOJI = "<:tick_yes:596096897995899097>"
    CROSS_MARK_EMOJI = "<:cross_no:596096897769275402>"

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.currently_setting_sonas = set()

    async def send_verification_message(
            self, user: discord.User, message: str, *, timeout: float = 600,
            check: callable = None, max_length: int = 200) -> discord.Message:
        """
        Sends a verification message to a user, waits for a response, and returns that message.
        """

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
        while True:
            try:
                v = await self.bot.wait_for(
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
            if len(v.content) > max_length:
                await user.send(f"The maximum length for this field is {max_length} (yours is at {len(v.content)}) - please send a shorter message.")
            else:
                return v

    @classmethod
    def get_image_from_message(cls, message: discord.Message) -> typing.Optional[str]:
        """
        Gets an image url from a given message.
        """

        if cls.is_image_url(message.content):
            return message.content
        if message.attachments and cls.is_image_url(message.attachments[0].url):
            return message.attachments[0].url
        return None

    @staticmethod
    def is_image_url(content: str) -> bool:
        """
        Returns whether a given string is a valid image url.
        """

        return re.search(r"^(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png|jpeg)$", content, re.IGNORECASE)

    @vbu.group(invoke_without_subcommand=True)
    @utils.checks.is_enabled_in_channel('disabled_sona_channels')
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def fursona(self, ctx: vbu.Context, user: typing.Optional[discord.Member], *, name: str = None):
        """
        Shows you someone's fursona.
        """

        if ctx.invoked_subcommand is not None:
            return
        await ctx.invoke(self.bot.get_command("fursona get"), user, name=name)

    @fursona.command(name="get")
    @utils.checks.is_enabled_in_channel('disabled_sona_channels')
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def fursona_get(self, ctx: vbu.Context, user: typing.Optional[discord.Member], *, name: str = None):
        """
        Shows you someone's fursona.
        """

        # Get the sonas
        user = user or ctx.author
        guild_id = ctx.guild.id
        if user.id == self.bot.user.id:
            guild_id = 0
        async with self.bot.database() as db:
            if name is None:
                rows = await db("SELECT * FROM fursonas WHERE guild_id=$1 AND user_id=$2", guild_id, user.id)
            else:
                rows = await db("SELECT * FROM fursonas WHERE guild_id=$1 AND user_id=$2 AND LOWER(name)=LOWER($3)", guild_id, user.id, name)

        # Check if they have a valid sona
        if not rows:
            return await ctx.send(f"{user.mention} has no sona set up on this server.")
        elif len(rows) > 1:
            available_sonas = [i['name'].replace('`', '\\`').replace('*', '\\*').replace('_', '\\_') for i in rows]
            available_string = ', '.join(f"`{name}`" for name in available_sonas)
            return await ctx.send(f"{user.mention} has more than one sona set - please get their sona using its name. Available sonas: {available_string}")
        if rows[0]['verified'] is False:
            return await ctx.send(f"{user.mention}'s sona has not yet been verified.")
        if rows[0]['nsfw'] is True and ctx.channel.nsfw is False:
            return await ctx.send("I can't show NSFW sonas in a SFW channel.")

        # Wew it's sona time let's go
        sona = utils.Fursona(**rows[0])
        return await ctx.send(embed=sona.get_embed(mention_user=True))

    @vbu.command(hidden=True, add_slash_command=False)
    @commands.check(utils.checks.is_verified)
    @vbu.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def setsona(self, ctx: vbu.Context):
        """
        Stores your fursona information in the bot.
        """

        await ctx.invoke(self.bot.get_command("fursona set"))

    @fursona.command(name="set")
    @commands.check(utils.checks.is_verified)
    @vbu.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def fursona_set(self, ctx: vbu.Context):
        """
        Stores your fursona information in the bot.
        """

        # See if the user already has a fursona stored
        async with self.bot.database() as db:
            rows = await db("SELECT * FROM fursonas WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, ctx.author.id)
        current_sona_names = [row['name'].lower() for row in rows]
        ctx.current_sona_names = current_sona_names

        # See if they're at the limit
        try:
            sona_limit = max(o for i, o in self.bot.guild_settings[ctx.guild.id].setdefault('role_sona_count', dict()).items() if int(i) in ctx.author._roles)
        except ValueError:
            sona_limit = 1
        if len(current_sona_names) >= sona_limit:
            return await ctx.send("You're already at the sona limit - you have to delete one to be able to set another.")

        # See if they're setting one up already
        if ctx.author.id in self.currently_setting_sonas:
            return await ctx.send("You're already setting up a sona! Please finish that one off first!")

        # Try and send them an initial DM
        user = ctx.author
        start_message = f"Now taking you through setting up your sona on **{ctx.guild.name}**!\n"
        if not self.bot.guild_settings[ctx.guild.id]["nsfw_is_allowed"]:
            start_message += f"NSFW fursonas are not allowed for **{ctx.guild.name}** and will be automatically declined.\n"
        try:
            await user.send(start_message.strip())
        except discord.Forbidden:
            return await ctx.send("I couldn't send you a DM! Please open your DMs for this server and try again.")
        self.currently_setting_sonas.add(user.id)
        await ctx.send("Sent you a DM!")

        # Ask about name
        name_message = await self.send_verification_message(user, "What is the name of your sona?")
        if name_message is None:
            return self.currently_setting_sonas.remove(user.id)
        if name_message.content.lower() in current_sona_names:
            self.currently_setting_sonas.remove(user.id)
            return await user.send(f"You already have a sona with the name `{name_message.content}`. Please start your setup again and provide a different name.")

        # Ask about gender
        gender_message = await self.send_verification_message(user, "What's your sona's gender?")
        if gender_message is None:
            return self.currently_setting_sonas.remove(user.id)

        # Ask about age
        age_message = await self.send_verification_message(user, "How old is your sona?")
        if age_message is None:
            return self.currently_setting_sonas.remove(user.id)

        # Ask about species
        species_message = await self.send_verification_message(user, "What species is your sona?")
        if species_message is None:
            return self.currently_setting_sonas.remove(user.id)

        # Ask about orientation
        orientation_message = await self.send_verification_message(user, "What's your sona's orientation?")
        if orientation_message is None:
            return self.currently_setting_sonas.remove(user.id)

        # Ask about height
        height_message = await self.send_verification_message(user, "How tall is your sona?")
        if height_message is None:
            return self.currently_setting_sonas.remove(user.id)

        # Ask about weight
        weight_message = await self.send_verification_message(user, "What's the weight of your sona?")
        if weight_message is None:
            return self.currently_setting_sonas.remove(user.id)

        # Ask about bio
        bio_message = await self.send_verification_message(user, "What's the bio of your sona?", max_length=1000)
        if bio_message is None:
            return self.currently_setting_sonas.remove(user.id)

        # Ask about image
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

        # Ask about NSFW
        if self.bot.guild_settings[ctx.guild.id]["nsfw_is_allowed"]:
            check = lambda m: isinstance(m.channel, discord.DMChannel) and m.author.id == user.id and m.content.lower() in ["yes", "no"]
            nsfw_message = await self.send_verification_message(user, "Is your sona NSFW? Please either say `yes` or `no`.", check=check)
            if nsfw_message is None:
                return self.currently_setting_sonas.remove(user.id)
            else:
                nsfw_content = nsfw_message.content.lower()
        else:
            nsfw_content = "no"

        # Format that into data
        image_content = None if image_message.content.lower() == "no" else self.get_image_from_message(image_message)
        information = {
            'name': name_message.content,
            'gender': gender_message.content,
            'age': age_message.content,
            'species': species_message.content,
            'orientation': orientation_message.content,
            'height': height_message.content,
            'weight': weight_message.content,
            'bio': bio_message.content,
            'image': image_content,
            'nsfw': nsfw_content == "yes",
        }
        self.currently_setting_sonas.remove(user.id)
        ctx.information = information
        if information['nsfw'] and not self.bot.guild_settings[ctx.guild.id]["nsfw_is_allowed"]:
            return await user.send("Your fursona has been automatically declined as it is NSFW")
        await self.bot.get_command("setsonabyjson").invoke(ctx)

    @vbu.command(hidden=True, add_slash_command=False)
    @vbu.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def setsonabyjson(self, ctx: vbu.Context, *, data: str = None):
        """
        Lets you set your sona with a JSON string.

        Valid keys are: name, gender, age, species, orientation, height, weight, bio, image, and nsfw.
        NSFW must be a boolean. All fields must be filled (apart from image, which must be a provided key but can contain
        a null value).
        """

        # Get current sona names
        current_sona_names = getattr(ctx, "current_sona_names", None)
        if current_sona_names is None:
            async with self.bot.database() as db:
                rows = await db("SELECT * FROM fursonas WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, ctx.author.id)
            current_sona_names = [row['name'].lower() for row in rows]

        # See if they're at the sona limit
        try:
            sona_limit = max(o for i, o in self.bot.guild_settings[ctx.guild.id].setdefault('role_sona_count', dict()).items() if int(i) in ctx.author._roles)
        except ValueError:
            sona_limit = 1
        if len(current_sona_names) >= sona_limit:
            return await ctx.send("You're already at the sona limit - you have to delete one to be able to set another.")

        # Load up the information
        information = getattr(ctx, 'information', None) or json.loads(data)
        information.update({
            'guild_id': ctx.guild.id,
            'user_id': ctx.author.id,
        })

        # See if they already have a sona with that name
        if information['name'].lower() in current_sona_names:
            return await ctx.author.send(f"You already have a sona with the name `{information['name']}`. Please start your setup again and provide a different name.")
        sona_object = utils.Fursona(**information)

        # Send it back to the user so we can make sure it sends
        user = ctx.author
        try:
            await user.send(embed=sona_object.get_embed())
        except discord.HTTPException as e:
            return await user.send(f"I couldn't send that embed to you - `{e}`. Please try again later.")

        # Send it to the verification channel
        guild_settings = self.bot.guild_settings[ctx.guild.id]
        modmail_channel_id = guild_settings.get("fursona_modmail_channel_id")
        modmail_message = None
        if modmail_channel_id:
            modmail_channel = self.bot.get_channel(modmail_channel_id)
            if modmail_channel is None:
                return await user.send(f"The moderators for the server **{ctx.guild.name}** have set their fursona modmail channel to an invalid ID - please inform them of such and try again later.")
            try:
                modmail_message = await modmail_channel.send(f"New sona submission from {user.mention}", embed=sona_object.get_embed())
            except discord.Forbidden:
                return await user.send(f"The moderators for the server **{ctx.guild.name}** have disallowed me from sending messages to their fursona modmail channel - please inform them of such and try again later.")
            try:
                await modmail_message.add_reaction("\N{HEAVY CHECK MARK}")
                await modmail_message.add_reaction("\N{HEAVY MULTIPLICATION X}")
                if self.bot.guild_settings[ctx.guild.id]["nsfw_is_allowed"]:
                    await modmail_message.add_reaction("\N{SMILING FACE WITH HORNS}")
            except discord.Forbidden:
                await modmail_message.delete()
                return await user.send(f"The moderators for the server **{ctx.guild.name}** have disallowed me from adding reactions in their fursona modmail channel - please inform them of such and try again later.")
        else:
            sona_object.verified = True  # Auto verify if there's no modmail channel

        # Save sona to database now it's sent properly
        async with self.bot.database() as db:
            try:
                await sona_object.save(db)
            except asyncpg.StringDataRightTruncationError:
                try:
                    await modmail_message.delete()
                except (AttributeError, discord.HTTPException):
                    pass
                return await user.send("I couldn't save your sona into the database - one of your provided values was too long to save.")

        # Tell them everything was done properly
        if modmail_channel_id:
            return await user.send("Your fursona has been sent to the moderators for approval! Please be patient as they review.")
        return await user.send("Your fursona has been saved!")

    @vbu.command(ignore_extra=False, add_slash_command=False)
    @vbu.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def deletesona(self, ctx: vbu.Context, *, name: str = None):
        """
        Deletes your sona.
        """

        await ctx.invoke(self.bot.get_command("fursona delete"), name=name)

    @fursona.command(ignore_extra=False, name="delete")
    @vbu.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    async def fursona_delete(self, ctx: vbu.Context, *, name: str = None):
        """
        Deletes your sona.
        """

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
            available_sonas = [i['name'].replace('`', '\\`').replace('*', '\\*').replace('_', '\\_') for i in rows]
            available_string = ', '.join(f"`{name}`" for name in available_sonas)
            return await ctx.send(f"You have multiple sonas - please specify which you want to delete. Available sonas: {available_string}")
        name = rows[0]['name']

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

    @vbu.Cog.listener("on_raw_reaction_add")
    async def fursona_verification_reaction_handler(self, payload: discord.RawReactionActionEvent):
        """
        Listens for reactions being added to fursona approval messages.
        """

        # Check not a bot
        if payload.user_id == self.bot.user.id:
            return
        guild = self.bot.get_guild(payload.guild_id) or await self.bot.fetch_guild(payload.guild_id)
        moderation_member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
        if moderation_member.bot:
            return

        # Check if we're in a modmail channel
        guild_settings = self.bot.guild_settings[payload.guild_id]
        modmail_channel_id = guild_settings.get("fursona_modmail_channel_id")
        if payload.channel_id != modmail_channel_id:
            return

        # Get the message
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        fursona_embed = message.embeds[0]

        # Make sure it's a sona
        if "new sona submission" not in message.content.lower():
            return
        if not fursona_embed.footer:
            return
        if not fursona_embed.footer.text.startswith("Fursona of"):
            return
        self.logger.info(f"Dealing with sona modmail on guild {payload.guild_id} with message {payload.message_id}")

        # Get the user ID
        try:
            fursona_user_id = int(fursona_embed.footer.text.split(' ')[2])
        except (AttributeError, ValueError):
            return  # TODO check the message was made by the bot
        fursona_name = fursona_embed.title
        fursona_member = guild.get_member(fursona_user_id) or await guild.fetch_member(fursona_user_id)
        if fursona_member is None:
            self.logger.info(f"No member could be found - message {payload.message_id}")
            return

        # See the mod's reaction
        emoji = str(payload.emoji)
        verified = False
        nsfw = False
        archive_channel_id = None
        delete_reason = "No reason provided"
        if emoji == "\N{HEAVY MULTIPLICATION X}":
            archive_channel_id = guild_settings.get("fursona_decline_archive_channel_id")
            bot_reason_question = await message.channel.send("Why are you declining that sona?")
            try:
                reason_message = await self.bot.wait_for("message", check=lambda m: m.author.id == payload.user_id and m.channel.id == payload.channel_id)
                delete_reason = reason_message.content
                await reason_message.delete(delay=1)
            except asyncio.TimeoutError:
                pass
            except discord.Forbidden:
                pass
            try:
                await bot_reason_question.delete()
            except discord.NotFound:
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
                if verified:
                    text = f"Sona of {fursona_member.mention} approved by <@{payload.user_id}>"
                    archive_embed = fursona_embed
                else:
                    text = f"Sona of {fursona_member.mention} declined by <@{payload.user_id}> with reason `{delete_reason}`."
                    archive_embed = None
                await archive_channel.send(text, embed=archive_embed, allowed_mentions=discord.AllowedMentions(users=False, everyone=False, roles=False))
            except (discord.Forbidden, AttributeError):
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
                await fursona_member.send(f"Your fursona, `{fursona_name}`, on **{fursona_member.guild.name}** has been declined, with the reason `{delete_reason}`.")
        except discord.Forbidden:
            pass


def setup(bot: vbu.Bot):
    x = FursonaCommands(bot)
    bot.add_cog(x)

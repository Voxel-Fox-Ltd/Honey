import typing
import asyncio
import collections

import discord
from discord.ext import tasks
import voxelbotutils as vbu


class VCLogs(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.queued_messages: typing.Dict[discord.Guild, typing.List[str]] = collections.defaultdict(list)
        self.queue_locks = collections.defaultdict(asyncio.Lock)
        self.send_queued_messages.start()

    def cog_unload(self):
        self.send_queued_messages.stop()

    @vbu.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """
        Log users joining or leaving VCs.
        """

        # If they didn't move
        if before.channel == after.channel:
            return

        # See if there's an update log
        update_log_id = self.bot.guild_settings[member.guild.id]['voice_update_modlog_channel_id']
        if not update_log_id:
            return
        channel = self.bot.get_channel(update_log_id)
        if not channel:
            return

        # Work out the text to send
        if before.channel is None:
            text = f"{member.mention} joined the **{after.channel.name}** VC."
        elif after.channel is None:
            text = f"{member.mention} left the **{before.channel.name}** VC."
        else:
            text = f"{member.mention} moved from the **{before.channel.name}** VC to the **{after.channel.name}** VC."

        # Queue the text
        async with self.queue_locks[member.guild]:
            self.queued_messages[member.guild].append(text)
        self.logger.info(f"Queued log update for VC user (G{member.guild.id}/U{member.id})")

    async def send_message_chunk(self, channel, text):
        if channel.permissions_for(channel.guild.me).embed_links:
            data = {"embed": vbu.Embed(use_random_colour=True, description=text)}
        else:
            data = {"content": text, "allowed_mentions": discord.AllowedMentions.none()}
        self.bot.create_task(channel.send(**data))

    @tasks.loop(seconds=10)
    async def send_queued_messages(self):
        """
        Send the queued messages to the guild's log.
        """

        # Get all valid guilds
        guild_text = {}

        # Get the text to be sent
        for guild, text_list in self.queued_messages.items():
            async with self.queue_locks[guild]:
                guild_text[guild] = text_list.copy()
                text_list.clear()

        # Work out where to send the things
        for guild, text_list in guild_text.items():
            if not text_list:
                continue
            update_log_id = self.bot.guild_settings[guild.id]['voice_update_modlog_channel_id']
            if not update_log_id:
                continue
            channel = self.bot.get_channel(update_log_id)
            if not channel:
                continue
            text = ""
            for line in text_list:
                if len(text) + len(line) >= 2_000:
                    await self.send_message_chunk(channel, text)
                    text = ""
                text += f"{line}\n"
            if text:
                await self.send_message_chunk(channel, text)

    @send_queued_messages.before_loop
    async def send_queued_messages_before_loop(self):
        await self.bot.wait_until_ready()


def setup(bot: vbu.Bot):
    x = VCLogs(bot)
    bot.add_cog(x)

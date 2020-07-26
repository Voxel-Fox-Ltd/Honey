from datetime import datetime as dt, timedelta

import discord

from cogs import utils


class MessageHandler(utils.Cog):

    def __init__(self, bot:utils.Bot):
        super().__init__(bot)
        self.last_audit_delete_entry_id = {}  # guild_id: (entry_id, count)

    @utils.Cog.listener()
    async def on_message_edit(self, before:discord.Message, after:discord.Message):
        """Logs edited messages"""

        # Filter
        if after.guild is None:
            return
        if before.content == after.content:
            return
        if not before.content or not after.content:
            return
        if after.author.bot:
            return

        # Create embed
        with utils.Embed(colour=0x0000ff) as embed:
            embed.set_author_to_user(user=after.author)
            embed.description = f"[Message edited]({after.jump_url}) in {after.channel.mention}"
            before_content = before.content
            if len(before.content) > 1000:
                before_content = before.content[:1000] + '...'
            after_content = after.content
            if len(after.content) > 1000:
                after_content = after.content[:1000] + '...'
            embed.add_field(name="Old Message", value=before_content, inline=False)
            embed.add_field(name="New Message", value=after_content, inline=False)
            embed.set_footer(f"User ID {after.author.id}")
            embed.timestamp = after.edited_at
            if after.attachments:
                embed.add_field("Attachments", '\n'.join([i.url for i in after.attachments]))

        # Get channel
        channel_id = self.bot.guild_settings[after.guild.id].get("edited_message_modlog_channel_id")
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            return

        # Send log
        try:
            m = await channel.send(embed=embed)
            self.logger.info(f"Logging edited message (G{m.guild.id}/C{m.channel.id})")
        except discord.Forbidden:
            pass

    @utils.Cog.listener()
    async def on_message_delete(self, message:discord.Message):
        """Logs edited messages"""

        # Filter
        if message.guild is None:
            return
        if message.author.bot:
            return

        # Create embed
        with utils.Embed(colour=0xff0000) as embed:
            embed.set_author_to_user(user=message.author)
            embed.description = f"Message deleted in {message.channel.mention}"
            if message.content:
                if len(message.content) > 1000:
                    embed.add_field(name="Message", value=message.content[:1000] + '...', inline=False)
                else:
                    embed.add_field(name="Message", value=message.content, inline=False)
            embed.set_footer(f"User ID {message.author.id}")
            embed.timestamp = dt.utcnow()
            if message.attachments:
                embed.add_field("Attachments", '\n'.join([f"[Attachment {index}]({i.url}) ([attachment {index} proxy]({i.proxy_url}))" for index, i in enumerate(message.attachments, start=1)]))

        # See if we can get who it was deleted by
        delete_time = dt.utcnow()
        if message.guild.me.guild_permissions.view_audit_log:
            changed = False
            async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=1):
                if entry.extra.channel.id != message.channel.id:
                    break
                if entry.target.id != message.author.id:
                    break
                if entry.extra.count == 1 and delete_time > entry.created_at + timedelta(seconds=0.1):
                    break  # I want the entry to be within 0.1 seconds of the message deletion
                elif entry.extra.count > 1:
                    last_delete_entry = self.last_audit_delete_entry_id.get(message.guild.id, (0, -1,))
                    if last_delete_entry[0] != entry.id:
                        break  # Last cached entry is DIFFERENT to this entry
                    if last_delete_entry[1] == entry.extra.count:
                        break  # Unchanged from last cached log
                self.last_audit_delete_entry_id[message.guild.id] = (entry.id, entry.extra.count)
                changed = True
                embed.description = f"Message deleted in {message.channel.mention} (deleted by {entry.user.mention})"
            if changed is False:
                embed.description = f"Message deleted in {message.channel.mention} (deleted by user or a bot)"

        # Get channel
        channel_id = self.bot.guild_settings[message.guild.id].get("deleted_message_modlog_channel_id")
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            return

        # Send log
        try:
            m = await channel.send(embed=embed)
            self.logger.info(f"Logging deleted message (G{m.guild.id}/C{m.channel.id})")
        except discord.Forbidden:
            pass


def setup(bot:utils.Bot):
    x = MessageHandler(bot)
    bot.add_cog(x)

import discord
import voxelbotutils as vbu


class VCLogs(vbu.Cog):

    @vbu.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """
        Log users joining or leaving VCs.
        """

        if before.channel == after.channel:
            return
        update_log_id = self.bot.guild_settings[member.guild.id]['voice_update_modlog_channel_id']
        if not update_log_id:
            return
        channel = self.bot.get_channel(update_log_id)
        if not channel:
            return
        try:
            if before.channel is None:
                text = f"{member.mention} joined the **{after.channel.name}** VC."
            elif after.channel is None:
                text = f"{member.mention} left the **{before.channel.name}** VC."
            else:
                text = f"{member.mention} moved from the **{before.channel.name}** VC to the **{after.channel.name}** VC."
            if channel.permissions_for(channel.guild.me).embed_links:
                data = {"embed": vbu.Embed(use_random_colour=True, description=text)}
            else:
                data = {"content": text, "allowed_mentions": discord.AllowedMentions(users=False)}
            await channel.send(**data)
            self.logger.info(f"Logging updated VC user (G{member.guild.id}/U{member.id})")
        except discord.Forbidden:
            pass


def setup(bot: vbu.Bot):
    x = VCLogs(bot)
    bot.add_cog(x)

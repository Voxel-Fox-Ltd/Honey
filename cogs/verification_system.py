import discord
from discord.ext import commands
import voxelbotutils as vbu


class VerificationSystem(vbu.Cog):

    @vbu.command()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(send_messages=True, manage_roles=True)
    async def verify(self, ctx: vbu.Context, user: discord.Member):
        """
        Adds the verified role to a user.
        """

        # Get the role
        verified_role_id = self.bot.guild_settings[ctx.guild.id].get("verified_role_id")
        if verified_role_id is None:
            self.logger.info(f"Verification attempt failed - no role set (G{ctx.guild.id})")
            return await ctx.send("There is no verified role set for this server.")
        verified_role = ctx.guild.get_role(verified_role_id)
        if verified_role is None:
            self.logger.info(f"Verification attempt failed - role set is deleted (G{ctx.guild.id})")
            return await ctx.send("The verified role for this server is set to a deleted role.")

        # See if they're already verified
        if verified_role in user.roles:
            return await ctx.send(f"{user.mention} is already verified.")

        # Role manage
        try:
            await user.add_roles(verified_role, reason=f"Verified by {ctx.author!s}")
        except discord.Forbidden as e:
            self.logger.info(f"Verification attempt failed, forbidden (G{ctx.guild.id}) - {e}")
            return await ctx.send(f"I was unable to add the verified role to {user.mention}.")
        except discord.NotFound as e:
            self.logger.error(f"Verification attempt failed (G{ctx.guild.id}) - {e}")
            return await ctx.send("To me it looks like that user doesn't exist :/")

        # Throw the reason into the database
        self.bot.dispatch("moderation_action", moderator=ctx.author, user=user, reason=None, action="Verify")

        # Output to chat
        self.logger.info(f"Verified user (G{ctx.guild.id}/U{user.id})")
        return await ctx.send(f"{user.mention} has been verified.")


def setup(bot: vbu.Bot):
    x = VerificationSystem(bot)
    bot.add_cog(x)

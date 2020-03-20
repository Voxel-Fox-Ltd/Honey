import discord
from discord.ext import commands

from cogs import utils


class Moderation(utils.Cog):

    @commands.command(cls=utils.Command)
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Adds a warning to a user"""

        #Chuck this bad boy in INFRACTIONS
        #Do things
        pass

    @commands.command(cls=utils.Command)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Kicks a user from the server"""

        #Chuck this bad boy in INFRACTIONS
        #Kick the user
        await ctx.guild.kick(user, reason)

    @commands.command(cls=utils.Command)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Bans a user from the server"""

        #Chuck this bad boy in INFRACTIONS
        #Kick the user
        await ctx.guild.ban(user, reason, delete_message_days=7)

def setup(bot:utils.Bot):
    x = Moderation(bot)
    bot.add_cog(x)

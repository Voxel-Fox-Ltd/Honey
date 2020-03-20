import string
import random
import datetime

import discord
from discord.ext import commands
from cogs import utils


class Moderation(utils.Cog):
    
    def __init__(self, bot:utils.Bot):
        super().__init__(bot)

    async def get_code(self, n:int=5) -> str:
        """This method creates a randomisied string to use as the infraction identifier.

        Input Argument: n - Must be int
        Returns: A string n long
        """

        def gen_code(n):
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))
        code = gen_code(n)
        async with self.bot.database() as db:
            is_valid = await db("SELECT infraction_id FROM infractions WHERE infraction_id = $1", code)
        if len(is_valid) == 0:
            return code

    @commands.command(cls=utils.Command)
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Adds a warning to a user"""

        #Chuck this bad boy in INFRACTIONS
        async with self.bot.database() as db:
            await db(
                f"""INSERT INTO infractions (infraction_id, guild_id, user_id, moderator_id, infraction_type, infraction_reason, timestamp)
                VALUES ($1, $2, 'warn', $3, $4)""",
                get_code(), ctx.guild.id, user.id, ctx.author.id, reason, datetime.datetime().now
            )
        #Do things
        await ctx.send(embed=discord.Embed(title="Warning Given", description=f"{user.mention} has been warned by {ctx.author.mention} for {reason}"))
        

    @commands.command(cls=utils.Command)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Kicks a user from the server"""

        #Chuck this bad boy in INFRACTIONS
        async with self.bot.database() as db:
            await db(
                f"""INSERT INTO infractions (infraction_id, guild_id, user_id, moderator_id, infraction_type, infraction_reason, timestamp)
                VALUES ($1, $2, 'kick', $3, $4)""",
                get_code(), ctx.guild.id, user.id, ctx.author.id, reason, datetime.datetime().now
            )
        #Kick the user
        await ctx.send(embed=discord.Embed(title="Kicked!", description=f"{user.mention} has been kicked by {ctx.author.mention} for {reason}"))
        await ctx.guild.kick(user, reason)

    @commands.command(cls=utils.Command)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx:utils.Context, user:discord.Member, *, reason:str='<No reason provided>'):
        """Bans a user from the server"""

        #Chuck this bad boy in INFRACTIONS
        async with self.bot.database() as db:
            await db(
                f"""INSERT INTO infractions (infraction_id, guild_id, user_id, moderator_id, infraction_type, infraction_reason, timestamp)
                VALUES ($1, $2, 'ban', $3, $4)""",
                get_code(), ctx.guild.id, user.id, ctx.author.id, reason, datetime.datetime().now
            )
        #Kick the user
        await ctx.send(embed=discord.Embed(title="Banned!", description=f"{user.mention} has been banned by {ctx.author.mention} for {reason}"))
        await ctx.guild.ban(user, reason, delete_message_days=7)

def setup(bot:utils.Bot):
    x = Moderation(bot)
    bot.add_cog(x)

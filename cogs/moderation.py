from discord.ext import commands

import discord
from cogs import utils


class Moderation(utils.Cog):

    # Warn Commands
    @commands.group(name="warn", cls=utils.Group)
    async def warn(self, ctx:utils.Context, user:discord.Member, *, reason:str):

        if ctx.invoked_subcommand is None:
            
            #Chuck this bad boy in INFRACTIONS

            #Do things
            pass


    @warn.command(name="add", cls=utils.Command)
    async def _add(self, ctx:utils.Context, user:discord.Member, *, reason:str):
        
        #Chuck this bad boy in INFRACTIONS


        #Do things
        pass

    @warn.command(name="remove", alias="rem", cls=utils.Command)
    async def _rem(self, ctx:utils.Context, user:discord.Member):
        
        #Chuck this bad boy in INFRACTIONS
        

        #Do things
        pass
    
    @warn.command(name="get", alias="fetch", cls=utils.Command)
    async def _get(self, ctx:utils.Context, user:discord.Member):
        
        #Grab INFRACTIONS
        

        #Do things
        pass

    

    # Kick Command
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.command(cls=utils.Command)
    async def kick(self, ctx:utils.Context, user:discord.Member, *, reason:str):
        
        #Chuck this bad boy in INFRACTIONS


        #Kick the user
        await ctx.guild.kick(user, reason)
    

    # Ban Command
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.command(cls=utils.Command)
    async def ban(self, ctx:utils.Context, user:discord.Member, *, reason:str):
        
        #Chuck this bad boy in INFRACTIONS


        #Kick the user
        await ctx.guild.ban(user, reason, delete_message_days=7)

def setup(bot:utils.Bot):
    x = Moderation(bot)
    bot.add_cog(x)

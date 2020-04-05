import discord
from discord.ext import commands


class MemberIsAuthorError(commands.BadArgument):
    pass


class NotAuthorMember(discord.Member):

    @classmethod
    async def convert(cls, ctx, value):
        member = await commands.MemberConverter().convert(ctx, value)
        if member.id == ctx.author.id:
            raise MemberIsAuthorError()
        return member

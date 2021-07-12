import random

import discord
from discord.ext import commands
import voxelbotutils as vbu


class MiscCommands(vbu.Cog):

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fakesona(self, ctx: vbu.Context):
        """
        Grabs you a fake sona from ThisFursonaDoesNotExist.com.
        """

        seed = random.randint(1, 99999)
        with vbu.Embed(use_random_colour=True) as embed:
            embed.set_author(name="Click here to it larger", url=f"https://thisfursonadoesnotexist.com/v2/jpgs-2x/seed{seed:0>5}.jpg")
            embed.set_image(f"https://thisfursonadoesnotexist.com/v2/jpgs/seed{seed:0>5}.jpg")
            embed.set_footer(text="Provided by ThisFursonaDoesNotExist.com")
        await ctx.send(embed=embed)

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True)
    async def poll(self, ctx: vbu.Context, *args):
        """
        Make a poll for a bunch of items.
        """

        if not args:
            raise vbu.errors.MissingRequiredArgumentString("args")
        if len(args) > 10:
            return await ctx.send("You can only pick 5 choices max per poll.")
        lines = [f"{index}\N{COMBINING ENCLOSING KEYCAP} {i}" for index, i in enumerate(args, start=1)]
        m = await ctx.send('\n'.join(lines), allowed_mentions=discord.AllowedMentions.none())
        for line in lines:
            await m.add_reaction(line.split(' ')[0])

    @vbu.command(aliases=['choice', 'choices'])
    @commands.bot_has_permissions(send_messages=True, add_reactions=True)
    async def choose(self, ctx: vbu.Context, *args):
        """
        Have the bot pick between several items.
        """

        if not args:
            raise vbu.errors.MissingRequiredArgumentString("args")
        return await ctx.send(f"I choose **{random.choice(args)}**.", allowed_mentions=discord.AllowedMentions.none())

    @vbu.command(aliases=["8ball"])
    @commands.bot_has_permissions(send_messages=True)
    async def eightball(self, ctx: vbu.Context, *, question: str):
        """
        Ask a question, get a slighty passive-aggressive response.
        """

        response = random.choice([
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes – definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ])
        if not question:
            raise vbu.errors.MissingRequiredArgumentString("question")
        return await ctx.send(response)


def setup(bot: vbu.Bot):
    x = MiscCommands(bot)
    bot.add_cog(x)

import asyncio
import random

import discord
from discord.ext import commands

from cogs import utils


class MiscCommands(utils.Cog):

    @commands.command(aliases=['git', 'code'], cls=utils.Command)
    @utils.checks.is_config_set('command_data', 'github')
    @commands.bot_has_permissions(send_messages=True)
    async def github(self, ctx:utils.Context):
        """Sends the GitHub Repository link"""

        await ctx.send(f"<{self.bot.config['command_data']['github']}>")

    @commands.command(aliases=['support', 'guild'], cls=utils.Command)
    @utils.checks.is_config_set('command_data', 'guild_invite')
    @commands.bot_has_permissions(send_messages=True)
    async def server(self, ctx:utils.Context):
        """Gives the invite to the support server"""

        await ctx.send(f"<{self.bot.config['command_data']['guild_invite']}>")

    @commands.command(aliases=['patreon'], cls=utils.Command)
    @utils.checks.is_config_set('command_data', 'patreon')
    @commands.bot_has_permissions(send_messages=True)
    async def donate(self, ctx:utils.Context):
        """Gives you the bot's creator's Patreon"""

        await ctx.send(f"<{self.bot.config['command_data']['patreon']}>")

    @commands.command(cls=utils.Command)
    @commands.bot_has_permissions(send_messages=True)
    @utils.checks.is_config_set('command_data', 'invite_command_enabled')
    async def invite(self, ctx:utils.Context):
        """Gives you the bot's invite link"""

        await ctx.send(f"<{self.bot.get_invite_link(embed_links=True, attach_files=True, manage_roles=True, kick_members=True, ban_members=True)}>")

    @commands.command(cls=utils.Command)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(send_messages=True)
    @utils.checks.is_config_set('command_data', 'echo_command_enabled')
    async def echo(self, ctx:utils.Context, *, content:str):
        """Echos the given content into the channel"""

        await ctx.send(content, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

    @commands.command(cls=utils.Command, aliases=['status'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @utils.checks.is_config_set('command_data', 'stats_command_enabled')
    async def stats(self, ctx:utils.Context):
        """Gives you the stats for the bot"""

        # Get creator info
        creator_id = self.bot.config["owners"][0]
        creator = self.bot.get_user(creator_id) or await self.bot.fetch_user(creator_id)

        # Make embed
        with utils.Embed(colour=0x1e90ff) as embed:
            embed.set_footer(str(self.bot.user), icon_url=self.bot.user.avatar_url)
            embed.add_field("Creator", f"{creator!s}\n{creator_id}")
            embed.add_field("Library", f"Discord.py {discord.__version__}")
            if self.bot.shard_count != len(self.bot.shard_ids):
                embed.add_field("Average Guild Count", int((len(self.bot.guilds) / len(self.bot.shard_ids)) * self.bot.shard_count))
            else:
                embed.add_field("Guild Count", len(self.bot.guilds))
            embed.add_field("Shard Count", self.bot.shard_count)
            embed.add_field("Average WS Latency", f"{(self.bot.latency * 1000):.2f}ms")
            embed.add_field("Coroutines", f"{len([i for i in asyncio.Task.all_tasks() if not i.done()])} running, {len(asyncio.Task.all_tasks())} total.")

        # Send it out wew let's go
        await ctx.send(embed=embed)

    @commands.command(cls=utils.Command)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fakesona(self, ctx:utils.Context):
        """Grabs you a fake sona from ThisFursonaDoesNotExist.com"""

        seed = random.randint(1, 99999)
        with utils.Embed(use_random_colour=True) as embed:
            embed.set_author(name="Click here to it larger", url=f"https://thisfursonadoesnotexist.com/v2/jpgs-2x/seed{seed:0>5}.jpg")
            embed.set_image(f"https://thisfursonadoesnotexist.com/v2/jpgs/seed{seed:0>5}.jpg")
            embed.set_footer(text="Provided by ThisFursonaDoesNotExist.com")
        await ctx.send(embed=embed)

    @commands.command(cls=utils.Command)
    @commands.bot_has_permissions(send_messages=True, add_reactions=True)
    async def poll(self, ctx:utils.Context, *args):
        """Make a poll for a bunch of items, seperated by 'or', eg 'this or that or thing'"""

        if not args:
            raise utils.errors.MissingRequiredArgumentString("args")
        if len(args) > 5:
            return await ctx.send("You can only pick 5 choices max per poll.")
        lines = [f"{index}\N{COMBINING ENCLOSING KEYCAP} {i}" for index, i in enumerate(args, start=1)]
        m = await ctx.send('\n'.join(lines))
        for line in lines:
            await m.add_reaction(line.split(' ')[0])

    @commands.command(cls=utils.Command, aliases=['choice', 'choices'])
    @commands.bot_has_permissions(send_messages=True, add_reactions=True)
    async def choose(self, ctx:utils.Context, *args):
        """Make a poll for a bunch of items, seperated by 'or', eg 'this or that or thing'"""

        if not args:
            raise utils.errors.MissingRequiredArgumentString("args")
        return await ctx.send(f"I choose **{random.choice(args)}**.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))


def setup(bot:utils.Bot):
    x = MiscCommands(bot)
    bot.add_cog(x)

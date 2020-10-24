
from cogs import utils


class ModMail(utils.Cog):

    @utils.Cog.listener("on_message")
    async def modmail_handler(self, message):

        ctx = await self.bot.get_context(message, cls=utils.Context)
        if ctx.command is not None or ctx.author.bot is True:
            return


def setup(bot: utils.Bot):
    x = ModMail(bot)
    bot.add_cog(x)
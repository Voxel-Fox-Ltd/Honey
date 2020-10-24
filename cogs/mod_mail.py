from cogs import utils


class ModMail(utils.Cog):

    ...


def setup(bot: utils.Bot):
    x = ModMail(bot)
    bot.add_cog(x)
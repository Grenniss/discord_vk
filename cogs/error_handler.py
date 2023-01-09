import traceback

from discord.ext import commands

from .utils.base_cog import BaseCog
from ..context import BotContext


class ErrorHandler(BaseCog):
    @commands.Cog.listener()
    async def on_command_error(self, ctx: BotContext, error: commands.CommandError):
        if isinstance(
            error,
            (
                commands.MissingRequiredArgument,
                commands.BadArgument,
                commands.CheckFailure,
            ),
        ):
            return await ctx.answer(str(error))

        formated_exc = traceback.format_exception(
            type(error), error, error.__traceback__
        )
        self.bot.logger.error("".join(formated_exc))


def setup(bot):
    bot.add_cog(ErrorHandler(bot))

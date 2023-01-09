import discord

from discord.ext import commands

from . import bot


class BotContext(commands.Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.bot: bot.Bot
        self.message: discord.Message
        self.phrases = self.bot.phrases

    async def answer(self, *args, **kwargs) -> discord.Message:
        ref = self.message.to_reference(fail_if_not_exists=False)
        return await self.send(*args, **kwargs, reference=ref, mention_author=True)

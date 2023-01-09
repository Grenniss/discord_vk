import logging

from typing import List

import discord

from discord.ext import commands

from . import config
from .phrases import ru
from .context import BotContext


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=get_command_prefix, intents=discord.Intents.all()
        )
        self.logger = logging.getLogger("bot")

    @property
    def config(self) -> config:
        return config

    @property
    def phrases(self) -> ru:
        return ru

    def run(self):
        super().run(self.config.bot_token, bot=True)

    async def close(self):
        for cog in self.cogs.values():
            await cog.on_bot_close()

        await super().close()

    async def process_commands(self, message: discord.Message):
        ctx: BotContext = await self.get_context(message, cls=BotContext)

        if ctx.command is None:
            return

        await self.invoke(ctx)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        await self.process_commands(message)

    async def on_ready(self):
        print(self.phrases.bot_started.format(bot=self))


async def get_command_prefix(bot: Bot, message: discord.Message) -> List[str]:
    return bot.config.command_prefixes

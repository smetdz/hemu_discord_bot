import os

import discord
from discord.ext import commands

import config
from cogs import events, fun, weather, welcome, anime, info
from twitch_notifier import TwitchNotifier


class HemuBot(commands.Bot):
    async def on_ready(self):
        twitch_notifier = TwitchNotifier(self)
        await twitch_notifier.notification()


if __name__ == '__main__':
    bot = HemuBot(command_prefix="!")

    cogs = [events, fun, weather, welcome, anime, info]

    for cog in cogs:
        cog.setup(bot)

    bot.run(os.environ['DISCORD_TOKEN'])

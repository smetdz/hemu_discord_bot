import os

import discord
from discord.ext import commands

import config
from cogs import events, fun, searches, welcome, anime, info
from twitch_notifier import TwitchNotifier


class HemuBot(commands.Bot):
    async def on_ready(self):
        twitch_notifier = TwitchNotifier(self)
        await twitch_notifier.notification()


if __name__ == '__main__':
    hemu = HemuBot(command_prefix="!")
    hemu.remove_command('help')

    cogs = [events, fun, searches, welcome, anime, info]

    for cog in cogs:
        cog.setup(hemu)

    hemu.run(os.environ['DISCORD_TOKEN'])

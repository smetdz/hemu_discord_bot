import os

import discord
from discord.ext import commands

import config
from cogs import events, fun, searches, welcome, anime, info, dev
from twitch_notifier import TwitchNotifier


class HemuBot(commands.Bot):
    async def on_ready(self):
        game = discord.Game("!help")
        await self.change_presence(status=discord.Status.online, activity=game)

        twitch_notifier = TwitchNotifier(self)
        await twitch_notifier.notification()


if __name__ == '__main__':
    hemu = HemuBot(command_prefix="!")
    hemu.remove_command('help')

    cogs = [events, fun, searches, welcome, anime, info, dev]

    for cog in cogs:
        cog.setup(hemu)

    hemu.run(os.environ['DISCORD_TOKEN'])

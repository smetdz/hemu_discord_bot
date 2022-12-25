import os
import pathlib
from collections import namedtuple

import discord
from discord.ext import commands
from umongo import fields

from mongo_documents import db, Guild, Reaction
from twitch_notifier import TwitchNotifier


class HemuBot(commands.Bot):
    db = None
    guilds_reactions = None
    guilds_reactions_status = None
    polls = {}
    list_views = {}
    reaction_tuple = namedtuple('rct', 'rct is_emb')

    async def on_ready(self):
        game = discord.Game("!help")
        await self.change_presence(status=discord.Status.online, activity=game)

        twitch_notifier = TwitchNotifier(self)
        await twitch_notifier.notification()

    async def load_reactions(self):
        guilds_ = Guild.find()
        guild_count = await Guild.count_documents()
        guilds = await guilds_.to_list(guild_count)
        print(guilds)

        reactions_ = Reaction.find()
        rcs_count = await Reaction.count_documents()
        g_reactions = await reactions_.to_list(rcs_count)
        print(g_reactions)

        ref = fields.Reference

        self.guilds_reactions_status = {guild.pk: guild.reactions_status for guild in guilds}

        self.guilds_reactions = {guild.title: {reaction.string: self.reaction_tuple(reaction.reaction, reaction.is_emb)
                                               for reaction in g_reactions if reaction.guild == ref(Guild, guild.pk)}
                                 for guild in guilds}

        print(self.guilds_reactions)

    def add_reaction(self, guild_name: str, string: str, reaction: str, is_emb: bool) -> None:
        self.guilds_reactions[guild_name][string] = self.reaction_tuple(rct=reaction, is_emb=is_emb)

    def remove_reaction(self, guild_name: str, string: str) -> None:
        self.guilds_reactions[guild_name].pop(string)


if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.members = True

    hemu = HemuBot(command_prefix="!", case_insensitive=True, intents=intents)
    hemu.remove_command('help')

    hemu.db = db
    hemu.loop.create_task(hemu.load_reactions())

    Path = pathlib.Path('hemu_discord_bot/cogs/')
    paths = list(Path.rglob('*.py'))

    modules = [str(path).split("/")[-1].strip('.py')
               for path in paths if not any(list(map(lambda s: s in str(path),
                                                     ['services', 'utils', 'notifications'])))]
    extensions = [f'cogs.{module}' for module in modules]
    print(extensions)

    for ext in extensions:
        hemu.load_extension(ext)

    hemu.run(os.environ['DISCORD_TOKEN'])

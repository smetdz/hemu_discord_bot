from pathlib import Path

import discord
from discord.ext import commands

import config
from utils import create_greeting


class HemuBot(commands.Bot):
    async def on_message(self, message):
        print(message.content, message.author.roles)
        if message.author == self.user:
            return

        key_words = {}

        if message.author.top_role.id == config.MODER_ROLE:
            test_commands = {
                '!testg': self.on_member_join,
                '!testr': self.on_member_remove,
            }

            key_words.update(test_commands)

        print(key_words)

        try:
            await key_words[message.content](message.author)
        except KeyError:
            await self.process_commands(message)

    @staticmethod
    async def on_member_remove(member: discord.Member):
        print(f'Member {member.name} left the server')
        chanel = list(filter(lambda ch: ch.name == '✋приветствие', member.guild.text_channels))[0]
        await chanel.send(f'Пользователь {member.name} покинул сервер.')

    @staticmethod
    async def on_member_join(member: discord.Member):
        print(f'New member {member.name}')
        chanel = list(filter(lambda ch: ch.name == '✋приветствие', member.guild.text_channels))[0]
        guild = member.guild

        emb_greeting = create_greeting(member, guild)

        await chanel.send(embed=emb_greeting)


bot = HemuBot(command_prefix="!")
bot.run(Path('TOKEN.txt').read_text())

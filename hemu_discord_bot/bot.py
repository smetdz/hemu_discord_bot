from pathlib import Path

import discord
from discord.ext import commands

from utils import create_greeting


class HemuBot(commands.Bot):
    async def on_message(self, message):
        print(message.content)
        if message.author == self.user:
            return

        if message.content == '!testg':
            chanel = list(filter(lambda ch: ch.name == '✋приветствие', message.guild.text_channels))[0]
            guild = message.guild

            emb_greeting = create_greeting(message.author, guild)

            await chanel.send(embed=emb_greeting)
        else:
            await self.process_commands(message)

    @staticmethod
    async def on_member_join(member: discord.Member):
        print(f'New member {member.name}')
        chanel = list(filter(lambda ch: ch.name == '✋приветствие', member.guild.text_channels))[0]
        guild = member.guild

        emb_greeting = create_greeting(member, guild)

        await chanel.send(embed=emb_greeting)


bot = HemuBot(command_prefix="!")
bot.run(Path('TOKEN.txt').read_text())

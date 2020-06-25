import os

import discord
from discord.utils import get
from discord.ext import commands

import config
from h_commands import CommandsList
from utils import create_greeting


class HemuBot(commands.Bot):
    async def on_message(self, message: discord.Message):
        print(message.content, message.author.roles)
        if message.author == self.user:
            return

        key_words = {}

        if message.author.top_role.id == config.MODER_ROLE:
            test_commands = {
                '!testg': self.on_member_join,
                '!testr': self.on_member_remove,
                '!testj': self.on_guild_join,
            }

            key_words.update(test_commands)

        print(key_words)

        try:
            await key_words[message.content](message.author)
        except AttributeError:
            await key_words[message.content](message.guild)
        except KeyError:
            await self.process_commands(message)

    @staticmethod
    async def on_guild_join(guild: discord.Guild):
        print(f'Join to server {guild.name}')
        chanel = get(guild.text_channels, id=config.channels['greeting_ch'])

        greeting_emb = discord.Embed(colour=discord.Color.dark_purple())
        greeting_emb.set_image(url=config.img_urls['server_join'])

        await chanel.send('**Всем привет, меня зовут Hemu-chan, надеюсь мы подружимся!~~**', embed=greeting_emb)

    @staticmethod
    async def on_member_remove(member: discord.Member):
        print(f'Member {member.name} left the server')
        chanel = get(member.guild.text_channels, id=config.channels['admin_ch'])
        await chanel.send(f'Пользователь {member.name} покинул сервер.')

    @staticmethod
    async def on_member_join(member: discord.Member):
        print(f'New member {member.name}')
        try:
            chanel = get(member.guild.text_channels, id=config.channels['greeting_ch'])
        except KeyError:
            chanel = member.guild.text_channels[0]

        guild = member.guild

        emb_greeting = create_greeting(member, guild)

        await chanel.send(embed=emb_greeting)


bot = HemuBot(command_prefix="!")
bot.add_cog(CommandsList(bot))
bot.run(os.environ['DISCORD_TOKEN'])

import discord
from discord.ext import commands
from discord.utils import get

import config
from cogs.utils import reactions


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        print(f'Member {member.name} left the server')

        try:
            chanel = get(member.guild.text_channels, id=config.channels['admin_ch'])
        except KeyError:
            chanel = member.guild.text_channels[0]

        await chanel.send(f'Пользователь {member.name} покинул сервер.')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        print(f'Author: {message.author}   Content: {message.content}')
        if message.author == self.bot.user:
            return

        await reactions(self.bot, message)

        # await self.bot.process_commands(message)


def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))

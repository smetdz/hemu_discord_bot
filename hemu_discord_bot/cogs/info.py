import json
import pathlib

import discord
from discord.ext import commands

from config import hemu_emoji
from bot import HemuBot
from cogs.utils.embeds import create_help_command_emb


class Info(commands.Cog):
    def __init__(self, bot: HemuBot):
        self.bot = bot

    @commands.command(name='help', aliases=('h', 'cmds', 'commands'))
    async def help(self, ctx: commands.Context, command_name: str = None, sub_command: str = None):
        path = pathlib.Path('hemu_discord_bot/resources/help.json')
        cogs_help = json.load(path.open(encoding='utf-8'))

        if command_name and not sub_command:
            current_command = self.find_command(cogs_help, command_name)

            if not current_command:
                await ctx.send(f'Не знаю такой команды как **{command_name}**,'
                               f' попробуй еще раз{hemu_emoji["sad_hemu"]}')
                return

            command_emb = create_help_command_emb(current_command, ctx.author.name)

            await ctx.send(embed=command_emb)
            return
        elif sub_command:
            current_command = self.find_command(cogs_help, command_name)
            try:
                c_sub_command = current_command['sub_commands'][sub_command]
            except KeyError:
                await ctx.send(f'Не знаю такой подкоманды как **{command_name}**,'
                               f' попробуй еще раз{hemu_emoji["sad_hemu"]}')
                return

            command_emb = create_help_command_emb(c_sub_command, ctx.author.name)

            await ctx.send(embed=command_emb)
            return

        commands_emb = discord.Embed(title='Список команд', colour=discord.Color.dark_purple())
        commands_emb.set_author(name='Hemu', icon_url=self.bot.user.avatar_url)

        for cog in cogs_help:
            commands_str = ', '.join([f'`{item["name"]}`' for _, item in cog['commands'].items()])
            commands_emb.add_field(inline=False, name=cog['cog_name'], value=commands_str)

        commands_emb.set_footer(text='Что бы узнать больше информации о команде,'
                                     ' используйте !help имя команды.')

        await ctx.send(embed=commands_emb)

    @staticmethod
    def find_command(cogs_help: dict, command_name):
        for cog in cogs_help:
            try:
                return cog['commands'][command_name]
            except KeyError:
                continue

        return None


def setup(bot: HemuBot):
    bot.add_cog(Info(bot))

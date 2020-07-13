import json
import datetime
import pathlib

import discord
from discord.ext import commands
from discord.utils import get

import config


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='роль', aliases=('role',))
    async def role_info(self, ctx: commands.Context, *, role_name: str = None):
        if role_name:
            try:
                role = list(ctx.message.role_mentions)[0]
            except IndexError:
                role = get(ctx.guild.roles, name=role_name)

                if not role:
                    await ctx.send(f'Роли "{role_name}" нет на сервере, попробуй еще раз.')
                    return

            role_emb = discord.Embed(title=f'Пользователи с ролью {role.name}', colour=role.colour,
                                     description=', '.join([member.name for member in role.members]))

            await ctx.send(embed=role_emb)

    @commands.command(name='help', aliases=('h', 'cmds', 'commands'))
    async def help(self, ctx: commands.Context, command_name: str = None):
        path = pathlib.Path('resources/help.json')
        cogs_help = json.load(path.open(encoding='utf-8'))

        if command_name:
            current_command = None
            for cog in cogs_help:
                for command in cog['commands']:
                    if command['name'] == command_name:
                        current_command = command

            if not current_command:
                await ctx.send(f'Не знаю такой команды как **{command_name}**,'
                               f' попробуй еще раз{config.emoji_dict["angry_hemu"]}')
                return

            command_emb = discord.Embed(title=f'Команда {command_name}', description=current_command['description'],
                                        colour=discord.Color.dark_purple())

            command_emb.add_field(inline=False, name='**Использование**', value=f'`{current_command["usage"]}`')

            if current_command['example']:
                command_emb.add_field(inline=False, name='**Пример**', value=f'`{current_command["example"]}`')

            if current_command['aliases']:
                command_emb.add_field(inline=False, name='**Псевдонимы**',
                                      value=", ".join([f"`{als}`" for als in current_command["aliases"]]),)

            command_emb.set_footer(text=f'Запрошено {ctx.author.name}')
            command_emb.timestamp = datetime.datetime.utcnow()

            await ctx.send(embed=command_emb)
            return

        commands_emb = discord.Embed(title='Список команд', colour=discord.Color.dark_purple())
        commands_emb.set_author(name='Hemu', icon_url=self.bot.user.avatar_url)

        for cog in cogs_help:
            commands_str = ', '.join([f'`{command["name"]}`' for command in cog['commands']])
            commands_emb.add_field(inline=False, name=cog['cog_name'], value=commands_str)

        commands_emb.set_footer(text='Что бы узнать больше информации о команде,'
                                     ' используйте !help имя команды.')

        await ctx.send(embed=commands_emb)


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))

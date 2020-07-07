import re
import datetime
import aiohttp

import discord
from discord.ext import commands

from cogs.anime_config import kinds, statuses


class Anime(commands.Cog):
    BASE_API_URL = 'https://shikimori.one/api'
    BASE_URL = 'https://shikimori.one'

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.shiki_icon = f'{self.BASE_URL}/favicon.ico'

    @commands.command(name='аниме')
    async def anime_rus(self, ctx: commands.Context, *, anime_name: str):
        await self.anime(ctx, anime_name)

    @commands.command(name='anime')
    async def anime_eng(self, ctx: commands.Context, *, anime_name: str):
        await self.anime(ctx, anime_name)

    async def anime(self, ctx: commands.Context, anime_name: str):
        anime = await self.get_title(anime_name.lower(), 'animes')
        print(anime)

        if anime:
            await self.return_title(ctx, 'anime', anime)
            return

        await ctx.send(f'Не могу найти аниме "**{anime_name}**". Попробуй еще раз.')

    @commands.command(name='манга')
    async def manga_ru(self, ctx: commands.Context, *, manga_name: str):
        await self.manga(ctx, manga_name)

    @commands.command(name='manga')
    async def manga_eng(self, ctx: commands.Context, *, manga_name: str):
        await self.manga(ctx, manga_name)

    async def manga(self, ctx: commands.Context, manga_name: str):
        manga = await self.get_title(manga_name.lower(), 'mangas')
        print(manga)

        if manga:
            await self.return_title(ctx, 'manga', manga)
            return

        await ctx.send(f'Не могу найти мангу "**{manga_name}**". Попробуй еще раз.')

    @commands.command(name='ранобэ')
    async def ranobe_ru(self, ctx: commands.Context, *, ranobe_name: str):
        await self.ranobe(ctx, ranobe_name)

    @commands.command(name='ranobe')
    async def ranobe_eng(self, ctx: commands.Context, *, ranobe_name: str):
        await self.ranobe(ctx, ranobe_name)

    async def ranobe(self, ctx: commands.Context, ranobe_name: str):
        ranobe = await self.get_title(ranobe_name.lower(), 'ranobe')
        print(ranobe)

        if ranobe:
            await self.return_title(ctx, 'ranobe', ranobe)
            return

        await ctx.send(f'Не могу найти ранобе "**{ranobe_name}**". Попробуй еще раз.')

    async def return_title(self, ctx: commands.Context, title_type: str, title: dict or list):
        message_type = {
            'anime': 'Найденные аниме',
            'manga': 'Найденная манга',
            'ranobe': 'Найденные ранобе',
        }

        if isinstance(title, list):
            titles_list = '\n'.join(title)
            emb = discord.Embed(title=f'{message_type[title_type]}:', colour=discord.Color.dark_purple(),
                                description=f'{titles_list}\n\n'
                                            f'Вызови команду и напиши название полностью.')
            await ctx.send(embed=emb)
            return
        elif isinstance(title, dict):
            title_emb = self.create_title_emb(title, title_type)
            await ctx.send(embed=title_emb)
            return

    async def get_title(self, title_name: str, api_type: str):
        async with aiohttp.ClientSession() as session:
            titles_list = await self.get_data(session, f'/{api_type}?search={title_name}&limit=10')

            current_title_ = None

            if not len(titles_list):
                return
            elif len(titles_list) - 1:
                for title in titles_list:
                    if title['name'].lower() == title_name or title['russian'].lower() == title_name:
                        current_title_ = title
                        break

                if not current_title_:
                    titles_names_list = [f'🔹{title["russian"]} / {title["name"]}' for title in titles_list]
                    return titles_names_list

            current_title_ = titles_list[0]
            title_id = current_title_['id']

            current_title = await self.get_data(session, f'/{api_type}/{title_id}')

        return current_title

    async def get_data(self, session: aiohttp.ClientSession, end_url: str):
        response = await session.get(url=f'{self.BASE_API_URL}{end_url}')
        return await response.json()

    def create_title_emb(self, title: dict, title_type: str):
        genres = ', '.join([genre['russian'] for genre in title['genres']]) + '.'

        try:
            description_ = re.sub(r'\[\[|]]', '', title['description'])
            description = re.sub(r'\[[^]]*]', '', description_)
        except TypeError:
            description = 'Описание отсутствует.'

        title_emb = discord.Embed(title=title['russian'], description=f'{description}\n\nЖанры: {genres}',
                                  url=f'{self.BASE_URL}/{title["url"]}', colour=discord.Color.dark_purple())

        try:
            title_emb.add_field(name='Тип', value=kinds[title_type][title['kind']])
        except KeyError:
            title_emb.add_field(name='Тип', value=title['kind'])

        title_emb.add_field(name='Рейтинг', value=title['score'])
        title_emb.add_field(name='Статус', value=statuses[title['status']])

        if title_type == 'anime':
            if title['status'] == 'ongoing':
                title_emb.add_field(name=f'Кол-во эпизодов',
                                    value=f'{title["episodes_aired"]}/'
                                          f'{title["episodes"] if int(title["episodes"]) else "?"}')
            else:
                title_emb.add_field(name='Кол-во эпизодов', value=title['episodes'])

            if title['kind'] in ['movie', 'music']:
                title_emb.add_field(name='Длительность', value=f'{str(title["duration"])} мин.')
            else:
                title_emb.add_field(name='Длительность эпизода', value=f'{title["duration"]} мин.')

            title_emb.add_field(name='Студия',
                                value=', '.join([studio['filtered_name']
                                                 for studio in title['studios']]) if title['studios'] else '-')
        else:
            title_emb.add_field(name='Тома', value=f'{title["volumes"] if title["volumes"] else "-"}')
            title_emb.add_field(name='Главы', value=f'{title["chapters"] if title["chapters"] else "-"}')
            title_emb.add_field(name='Издатель',
                                value=', '.join([publisher['name']
                                                 for publisher in title['publishers']]) if title['publishers'] else '-')

        title_emb.set_thumbnail(url=f'{self.BASE_URL}/{title["image"]["original"]}')
        title_emb.set_footer(icon_url=self.shiki_icon, text='Shikimori')
        title_emb.timestamp = datetime.datetime.utcnow()

        return title_emb


def setup(bot: commands.Bot):
    bot.add_cog(Anime(bot))

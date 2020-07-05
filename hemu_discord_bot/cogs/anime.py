import re
import datetime
import aiohttp

import discord
from discord.ext import commands


class Anime(commands.Cog):
    BASE_API_URL = 'https://shikimori.one/api'
    BASE_URL = 'https://shikimori.one'

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.shiki_icon = f'{self.BASE_URL}/favicon.ico'

    @commands.command(name='аниме')
    async def anime(self, ctx: commands.Context, *, anime_name: str):
        anime = await self.get_anime(anime_name.lower())

        print(anime)

        if anime:
            if isinstance(anime, list):
                anime_list = '\n'.join(anime)
                emb = discord.Embed(title='Найденные аниме:', colour=discord.Color.dark_purple(),
                                    description=f'{anime_list}\n\n'
                                                f'Вызови команду и напиши название полностью.')
                await ctx.send(embed=emb)
                return
            elif isinstance(anime, dict):
                anime_emb = self.create_anime_emb(anime)
                await ctx.send(embed=anime_emb)
                return

        await ctx.send(f'Не могу найти аниме "**{anime_name}**". Попробуй еще раз.')

    async def get_anime(self, anime_name: str):
        async with aiohttp.ClientSession() as session:
            anime_list = await self.get_data(session, f'/animes?search={anime_name}&limit=10')

            current_anime_ = None

            if not len(anime_list):
                return
            elif len(anime_list) - 1:
                for anime in anime_list:
                    if anime['name'].lower() == anime_name or anime['russian'].lower() == anime_name:
                        current_anime_ = anime
                        break

                if not current_anime_:
                    anime_names_list = [anime['russian'] for anime in anime_list]
                    return anime_names_list

            current_anime_ = anime_list[0]
            anime_id = current_anime_['id']

            current_anime = await self.get_data(session, f'/animes/{anime_id}')

        return current_anime

    async def get_data(self, session: aiohttp.ClientSession, end_url: str):
        response = await session.get(url=f'{self.BASE_API_URL}{end_url}')
        return await response.json()

    def create_anime_emb(self, anime: dict):
        kinds = {
            'movie': 'Фильм',
            'tv': 'TV Сериал',
            'music': 'Клип',
            'ova': 'OVA',
            'ona': 'ONA',
            'special': 'Спешл',
        }

        statuses = {
            'released': 'Вышло',
            'ongoing': 'Онгоинг',
            'anons': 'Анонс',
        }

        genres = ', '.join([genre['russian'] for genre in anime['genres']]) + '.'

        try:
            description_ = re.sub(r'\[\[|]]', '', anime['description'])
            description = re.sub(r'\[[^]]*]', '', description_)
        except TypeError:
            description = 'Описание отсутствует.'

        anime_emb = discord.Embed(title=anime['russian'], description=f'{description}\n\nЖанры: {genres}',
                                  url=f'{self.BASE_URL}/{anime["url"]}', colour=discord.Color.dark_purple())

        try:
            anime_emb.add_field(name='Тип', value=kinds[anime['kind']])
        except KeyError:
            anime_emb.add_field(name='Тип', value=anime['kind'])

        anime_emb.add_field(name='Рейтинг', value=anime['score'])
        anime_emb.add_field(name='Статус', value=statuses[anime['status']])

        if anime['status'] == 'ongoing':
            anime_emb.add_field(name='Кол-во эпизодов',
                                value=f'{anime["episodes_aired"]}/'
                                      f'{anime["episodes"] if int(anime["episodes"]) else "?"}')
        else:
            anime_emb.add_field(name='Кол-во эпизодов', value=anime['episodes'])

        if anime['kind'] in ['movie', 'music']:
            anime_emb.add_field(name='Длительность', value=f'{anime["duration"]} мин.')
        else:
            anime_emb.add_field(name='Длительность эпизода', value=f'{anime["duration"]} мин.')

        anime_emb.add_field(name='Студия', value=', '.join([studio['filtered_name'] for studio in anime['studios']]))

        anime_emb.set_thumbnail(url=f'{self.BASE_URL}/{anime["image"]["original"]}')
        anime_emb.set_footer(icon_url=self.shiki_icon, text='Shikimori')
        anime_emb.timestamp = datetime.datetime.utcnow()

        return anime_emb


def setup(bot: commands.Bot):
    bot.add_cog(Anime(bot))

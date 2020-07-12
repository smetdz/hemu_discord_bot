import datetime
from typing import Union

import discord

from cogs.services.openweather import Weather
from cogs.services.shikimori import Anime, Manga, Ranobe


def create_weather_emb(city: str, weather: Weather):
    weather_emb = discord.Embed(title=f'**{weather.description.title()}**',
                                colour=discord.Color.dark_purple())

    weather_emb.set_author(name=f'{city}'.title())

    weather_emb.set_thumbnail(url=weather.weather_icon)

    weather_emb.add_field(name='Температура', value=f'{weather.temp} °C')
    weather_emb.add_field(name='Макс. температура', value=f'{weather.temp_max} °C')
    weather_emb.add_field(name='Давление', value=f'{weather.pressure}  мбар')
    weather_emb.add_field(name='Ощущается как', value=f'{weather.feels_like} °C')
    weather_emb.add_field(name='Мин. температура', value=f'{weather.temp_min} °C')
    weather_emb.add_field(name='Влажность', value=f'{weather.humidity}%')

    weather_emb.set_footer(text='OpenWeather', icon_url=weather.logo)

    weather_emb.timestamp = datetime.datetime.utcnow()

    return weather_emb


def create_title_emb(title: Union[Anime, Manga, Ranobe]):
    genres = ', '.join([genre for genre in title.genres]) + '.'

    title_emb = discord.Embed(title=title.title_name, description=f'{title.description}\n\nЖанры: {genres}',
                              url=title.url, colour=discord.Color.dark_purple())

    title_emb.add_field(name='Тип', value=title.kind)
    title_emb.add_field(name='Рейтинг', value=title.score)
    title_emb.add_field(name='Статус', value=title.status)

    if isinstance(title, Anime):
        if title.status == 'Онгоинг':
            title_emb.add_field(name=f'Кол-во эпизодов',
                                value=f'{title.episodes_aired}/'
                                      f'{title.episodes if int(title.episodes) else "?"}')
        else:
            title_emb.add_field(name='Кол-во эпизодов', value=title.episodes)

        if title.kind in ['movie', 'music']:
            title_emb.add_field(name='Длительность', value=f'{str(title.duration)} мин.')
        else:
            title_emb.add_field(name='Длительность эпизода', value=f'{title.duration} мин.')

        title_emb.add_field(name='Студия',
                            value=', '.join([studio['filtered_name']
                                             for studio in title.studios]) if title.studios else '-')
    else:
        title_emb.add_field(name='Тома', value=f'{title.volumes if title.volumes else "-"}')
        title_emb.add_field(name='Главы', value=f'{title.chapters if title.chapters else "-"}')
        title_emb.add_field(name='Издатель',
                            value=', '.join([publisher['name']
                                             for publisher in title.publishers]) if title.publishers else '-')

    title_emb.set_thumbnail(url=title.image)
    title_emb.set_footer(icon_url=title.logo_icon, text='Shikimori')
    title_emb.timestamp = datetime.datetime.utcnow()

    return title_emb

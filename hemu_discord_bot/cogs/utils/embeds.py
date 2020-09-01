import datetime
from typing import Union

import discord

from cogs.services.openweather import Weather
from cogs.services.shikimori import Anime, Manga, Ranobe, Character


def create_help_command_emb(current_command: dict, author) -> discord.Embed:
    command_emb = discord.Embed(title=f'Команда {current_command["name"]}',
                                description=current_command['description'],
                                colour=discord.Color.dark_purple())

    try:
        command_emb.add_field(inline=False, name='**Подкоманды**',
                              value=", ".join([f"`{sub_command['name']}`"
                                               for sub_command in current_command['sub_commands']]))
    except KeyError:
        pass

    command_emb.add_field(inline=False, name='**Использование**', value=f'`{current_command["usage"]}`')

    if current_command['example']:
        command_emb.add_field(inline=False, name='**Пример**', value=f'`{current_command["example"]}`')

    if current_command['aliases']:
        command_emb.add_field(inline=False, name='**Псевдонимы**',
                              value=", ".join([f"`{als}`" for als in current_command["aliases"]]), )

    command_emb.set_footer(text=f'Запрошено {author}')
    command_emb.timestamp = datetime.datetime.utcnow()

    return command_emb


def create_weather_emb(city: str, weather: Weather) -> discord.Embed:
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


def create_title_emb(title: Union[Anime, Manga, Ranobe]) -> discord.Embed:
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


def create_char_emb(character: Character) -> discord.Embed:
    char_emb = discord.Embed(title=character.name, url=character.url, description=character.description,
                             colour=discord.Color.dark_purple())

    char_emb.add_field(inline=False, name='Аниме',
                       value=create_field_value([anime['russian']
                                                 for anime in character.animes], 200) if character.animes else '-')
    char_emb.add_field(inline=False, name='Манга',
                       value=create_field_value([manga['russian']
                                                 for manga in character.mangas
                                                 if manga["kind"] == "manga"], 200) if character.mangas else '-')

    char_emb.add_field(inline=False, name='Ранобэ',
                       value=create_field_value([manga['russian']
                                                 for manga in character.mangas
                                                 if manga["kind"] == "novel"], 200) if character.mangas else '-')

    char_emb.set_thumbnail(url=character.image)
    char_emb.set_footer(icon_url=character.logo_icon, text='Shikimori')
    char_emb.timestamp = datetime.datetime.utcnow()

    return char_emb


def create_field_value(value_list: list, limit: int) -> str:
    value = ''
    for val in value_list:
        if len(value + val + ', ') < limit:
            value += val + ', '
            continue
        return value + '...'

    return value[:-2] + '.'

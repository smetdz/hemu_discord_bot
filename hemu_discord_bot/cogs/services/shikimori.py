import re
from typing import Union

import aiohttp


class ShikimoriRef:
    BASE_API_URL = 'https://shikimori.one/api'
    BASE_URL = 'https://shikimori.one'
    logo_icon = f'{BASE_URL}/favicon.ico'

    endpoints = {
        'anime': 'animes',
        'manga': 'mangas',
        'ranobe': 'ranobe',
        'character': 'characters',
    }

    def __init__(self):
        self.info_types = {
            'anime': Anime,
            'manga': Manga,
            'ranobe': Ranobe,
            'character': Character,
        }

    async def get_info(self, name: str, info_type: str = None):
        async with aiohttp.ClientSession() as session:
            if info_type == 'character':
                info_list = await self._get_data(session, f'/{self.endpoints[info_type]}/search?search={name}')
            else:
                info_list = await self._get_data(session, f'/{self.endpoints[info_type]}?search={name}&limit=10')

            current_info_ = None

            if not len(info_list):
                return
            elif len(info_list) - 1:
                for item in info_list:
                    if item['name'].lower() == name or item['russian'].lower() == name:
                        current_info_ = item
                        break

                if not current_info_:
                    items_names_list = [f'🔹{title["russian"]} / {title["name"]}' for title in info_list]
                    return items_names_list

            current_info_ = info_list[0]
            item_id = current_info_['id']

            current_info = await self._get_data(session, f'/{self.endpoints[info_type]}/{item_id}')

        current_info['image'] = f'{self.BASE_URL}/{current_info["image"]["original"]}'
        current_info['url'] = f'{self.BASE_URL}/{current_info["url"]}'
        return self.info_types[info_type](logo_icon=f'{self.BASE_URL}/favicon.ico', **current_info)

    async def _get_data(self, session: aiohttp.ClientSession, end_url: str):
        response = await session.get(url=f'{self.BASE_API_URL}{end_url}')
        return await response.json()


class Title:
    statuses = {
        'released': 'Вышло',
        'ongoing': 'Онгоинг',
        'anons': 'Анонс',
        'paused': 'Приостановлено',
        'discontinued': 'Прекращено',
    }

    def __init__(self, **kwargs):
        self.title_name = kwargs['russian']
        self.genres = [genre['russian'] for genre in kwargs['genres']]
        self.url = kwargs['url']

        try:
            description_ = re.sub(r'\[\[|]]', '', kwargs['description'])
            self.description = re.sub(r'\[[^]]*]', '', description_)
        except TypeError:
            self.description = 'Описание отсутствует.'

        self.image = kwargs['image']
        self.logo_icon = kwargs['logo_icon']
        self.score = kwargs['score']
        self.status = self.statuses[kwargs['status']]

    def __str__(self):
        return '\n'.join([f'{key}: {value}' for key, value in self.__dict__.items()])


class Anime(Title):
    kinds = {
        'movie': 'Фильм',
        'tv': 'TV Сериал',
        'music': 'Клип',
        'ova': 'OVA',
        'ona': 'ONA',
        'special': 'Спешл',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        try:
            self.kind = self.kinds[kwargs['kind']]
        except KeyError:
            self.kind = kwargs['kind']

        self.episodes_aired = kwargs['episodes_aired']
        self.episodes = kwargs['episodes']
        self.duration = kwargs['duration']
        self.studios = kwargs['studios']


class Manga(Title):
    kinds = {
        'manga': 'Манга',
        'manhwa': 'Манхва',
        'manhua': 'Маньхуа',
        'one_shot': 'Ваншот',
        'doujin': 'Додзинси',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        try:
            self.kind = self.kinds[kwargs['kind']]
        except KeyError:
            self.kind = kwargs['kind']

        self.volumes = kwargs['volumes']
        self.chapters = kwargs['chapters']
        self.publishers = kwargs['publishers']


class Ranobe(Title):
    kinds = {
        'novel': 'Ранобе',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        try:
            self.kind = self.kinds[kwargs['kind']]
        except KeyError:
            self.kind = kwargs['kind']

        self.volumes = kwargs['volumes']
        self.chapters = kwargs['chapters']
        self.publishers = kwargs['publishers']


class Character:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.url = kwargs['url']
        self.image = kwargs['image']
        self.description = kwargs['description']

        try:
            description_ = re.sub(r'\[\[|]]', '', kwargs['description'])
            description_ = re.sub(r'\[spoiler=[^]]*]|\[/spoiler]', '||', description_)
            self.description = re.sub(r'\[[^]]*]', '', description_)
        except TypeError:
            self.description = 'Описание отсутствует.'

        self.animes = kwargs['animes']
        self.mangas = kwargs['mangas']
        self.logo_icon = kwargs['logo_icon']

    def __str__(self):
        return '\n'.join([f'{key}: {value}' for key, value in self.__dict__.items()])

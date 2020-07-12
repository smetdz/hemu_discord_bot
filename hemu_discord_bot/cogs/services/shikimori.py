import re

import aiohttp


class ShikimoriRef:
    BASE_API_URL = 'https://shikimori.one/api'
    BASE_URL = 'https://shikimori.one'
    logo_icon = f'{BASE_URL}/favicon.ico'

    endpoints = {
        'anime': 'animes',
        'manga': 'mangas',
        'ranobe': 'ranobe',
    }

    def __init__(self):
        self.title_types = {
            'anime': Anime,
            'manga': Manga,
            'ranobe': Ranobe,
        }

    async def get_title(self, title_name: str, title_type: str):
        async with aiohttp.ClientSession() as session:
            titles_list = await self.get_data(session, f'/{self.endpoints[title_type]}?search={title_name}&limit=10')

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

            current_title = await self.get_data(session, f'/{self.endpoints[title_type]}/{title_id}')

        current_title['image'] = f'{self.BASE_URL}/{current_title["image"]["original"]}'
        current_title['url'] = f'{self.BASE_URL}/{current_title["url"]}'
        return self.title_types[title_type](logo_icon=f'{self.BASE_URL}/favicon.ico', **current_title)

    async def get_data(self, session: aiohttp.ClientSession, end_url: str):
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

import os

import aiohttp


TENOR_ICON = 'https://tenor.com/assets/img/favicon/apple-touch-icon-72x72.png'


class TenorRef:
    BASE_API_URL = 'https://api.tenor.com/v1'
    API_KEY = os.environ['TENOR_KEY']

    async def search_gifs(self, search_str: str, limit: int = 50):
        endpoint = 'search'
        media_filter = 'minimal'

        return await self.get_results(search_str, endpoint, media_filter, limit)

    async def get_gifs_list(self, search_str: str):
        results = await self.search_gifs(search_str)
        return [res['media'][0]['gif']['url'] for res in results]

    async def get_random_gif(self, search_str: str, limit: int = 1):
        endpoint = 'random'
        media_filter = 'minimal'

        result = await self.get_results(search_str, endpoint, media_filter, limit)
        return result[0]['media'][0]['gif']['url']

    async def get_results(self, search_str: str, endpoint: str, media_filter: str, limit: int):
        url = f'{self.BASE_API_URL}/{endpoint}?' \
              f'key={self.API_KEY}&' \
              f'q={search_str}&' \
              f'limit={limit}&' \
              f'media_filter={media_filter}'

        return (await self.get_data(url))['results']

    @staticmethod
    async def get_data(url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                return await response.json()

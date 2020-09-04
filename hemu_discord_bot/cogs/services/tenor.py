import os

import aiohttp


TENOR_ICON = 'https://tenor.com/assets/img/favicon/apple-touch-icon-72x72.png'


class TenorRef:
    BASE_API_URL = 'https://api.tenor.com/v1'
    API_KEY = os.environ['TENOR_KEY']

    async def search_gifs(self, search_str: str, limit: int = 50):
        endpoint = 'search'
        media_filter = 'minimal'

        url = f'{self.BASE_API_URL}/{endpoint}?' \
              f'key={self.API_KEY}&' \
              f'q={search_str}&' \
              f'limit={limit}&' \
              f'media_filter={media_filter}'

        return (await self.get_data(url))['results']

    async def get_gifs_list(self, search_str: str):
        results = await self.search_gifs(search_str)
        return [res['media'][0]['gif']['url'] for res in results]

    @staticmethod
    async def get_data(url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                return await response.json()

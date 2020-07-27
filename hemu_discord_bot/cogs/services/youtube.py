import os
import datetime

import aiohttp

from cogs.utils.errors import VideoDoesNotExist


class YouTubeRef:
    BASE_URL = 'https://www.youtube.com/'
    BASE_API_URL = 'https://www.googleapis.com/youtube/v3'
    api_key = os.environ['YOUTUBE_KEY']

    async def get_channel_by_name(self, channel_title: str):
        data = await self._get_data(f'/search?key={self.api_key}&q={channel_title}&type=channel')

        try:
            channel_data = data['items'][0]
        except IndexError:
            return

        channel_id = channel_data['id']['channelId']

        video = await self.get_last_channel_video(channel_id)

        return YouTubeChannel(video, title=channel_title, channel_id=channel_id)

    async def get_last_channel_video(self, channel_id: str):
        data = await self._get_data(f'/search?key={self.api_key}&channelId={channel_id}'
                                    f'&part=snippet,id&order=date&maxResults=50')

        try:
            video_data = data['items'][0]
        except IndexError:
            return

        return YouTubeVideo(video_id=video_data['id']['videoId'], published_at=video_data['snippet']['publishedAt'])

    async def _get_data(self, endpoint: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=f'{self.BASE_API_URL}{endpoint}') as response:
                return await response.json()

    async def get_video(self, video_title: str):
        data = await self._get_data(f'/search?key={self.api_key}&q={video_title}')

        try:
            video_data = data['items'][0]
        except IndexError:
            raise VideoDoesNotExist

        return YouTubeVideo(video_id=video_data['id']['videoId'])


class YouTubeChannel:
    def __init__(self, last_video, **kwargs):
        self.title = kwargs['title']
        self.channel_id = kwargs['channel_id']
        self.last_video = last_video


class YouTubeVideo:
    BASE_URL = 'https://www.youtube.com/'

    def __init__(self, **kwargs):
        self.id = kwargs['video_id']
        try:
            self.published_at = datetime.datetime.strptime(kwargs['published_at'], '%Y-%m-%dT%H:%M:%SZ')
        except KeyError:
            self.published_at = None

    @property
    def video_url(self):
        return f'{self.BASE_URL}/watch?v={self.id}'

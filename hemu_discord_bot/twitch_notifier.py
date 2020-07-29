import os
import aiohttp
import asyncio

import discord
from discord.ext import commands

import config


class TwitchNotifier:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._stream_status = False
        self._channel = 'cletusfindlay'
        self._oauth_token = ''
        self._urls = {
            'channel': 'https://api.twitch.tv/helix/search/channels?query=',
            'user': 'https://api.twitch.tv/helix/users?login=',
            'basic': 'https://www.twitch.tv/',
        }

    async def notification(self):
        async with aiohttp.ClientSession() as session:
            while True:
                channel_data = await self.get_data('channel', session)

                if not channel_data:
                    continue

                if channel_data['is_live'] == self._stream_status:
                    delay = 60
                else:
                    channel = self.bot.get_channel(config.channels['news'])
                    user_data = await self.get_data('user', session)

                    if self._stream_status:
                        twitch_emb = self.create_twitch_embed(channel_data, user_data, False)
                        try:
                            await message.edit(content='', embed=twitch_emb)
                        except Exception as e:
                            print(e)
                        await channel.send('Стрим закончился')
                    else:
                        twitch_emb = self.create_twitch_embed(channel_data, user_data)
                        message = await channel.send('@everyone', embed=twitch_emb)

                    delay = 120
                    self._stream_status = not self._stream_status

                await asyncio.sleep(delay)

    async def get_data(self, data_type: str, session: aiohttp.ClientSession):
        headers = {'Client-ID': config.TWITCH_CLIENT_ID,
                   'Authorization': f'Bearer {self._oauth_token}'}
        response = await session.get(url=self._urls[data_type] + self._channel, headers=headers)

        if response.status == 401:
            await self.get_oauth_token(session)
            return

        data_ = await response.json()
        data = data_['data'][0]
        print(f'{data_type}:\n{data}')

        return data

    async def get_oauth_token(self, session: aiohttp.ClientSession):
        response = await session.post(url=f'https://id.twitch.tv/oauth2/token'
                                          f'?client_id={config.TWITCH_CLIENT_ID}'
                                          f'&client_secret={os.environ["TWITCH_CLIENT_SECRET"]}'
                                          f'&grant_type=client_credentials')

        data_json = await response.json()
        self._oauth_token = data_json['access_token']

    def create_twitch_embed(self, channel_data: dict, user_data: dict, started: bool = True) -> discord.Embed:
        title = channel_data['title'] if started else 'Стрим не в сети'

        twitch_emb = discord.Embed(title=title, url=f'{self._urls["basic"] + self._channel}',
                                   colour=discord.Color.dark_purple())
        twitch_emb.set_author(name=user_data['display_name'], icon_url=user_data['profile_image_url'])
        twitch_emb.set_image(url=user_data['offline_image_url'])

        return twitch_emb




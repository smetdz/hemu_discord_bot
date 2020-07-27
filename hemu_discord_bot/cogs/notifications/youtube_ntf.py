import asyncio
from datetime import datetime

import discord
from discord.ext import tasks

from bot import HemuBot
from cogs.services.youtube import YouTubeRef, YouTubeChannel as YouTubeChannelRef, YouTubeVideo
from mongo_documents import YouTubeChannel as YouTubeChannelDoc, fields
from cogs.utils.errors import ChannelAlreadyExist, ChannelDoesNotExist
from cogs.notifications.base import YouTubeChannel, Guild


class YouTubeNotifier:
    channels_dict = {}

    def __init__(self, bot: HemuBot):
        self.bot = bot
        self.youtube = YouTubeRef()
        self.bot.loop.create_task(self.load_channels())

    @staticmethod
    def data_to_dict(y_ch: YouTubeChannelDoc, guilds: list):
        c_dict = {
            'title': y_ch.title,
            'channel_id': y_ch.pk,
            'last_video_id': y_ch.last_video_id,
            'guilds': [Guild(guild_id=guild['guild_id'], channel_id=guild['channel_id'], role_id=guild['role_id'])
                       for guild in guilds]
        }

        return c_dict

    async def load_channels(self):
        doc_channels = YouTubeChannelDoc.find()
        doc_count = await YouTubeChannelDoc.count_documents()
        youtube_channels = await doc_channels.to_list(doc_count)

        self.channels_dict = {y_ch.title: YouTubeChannel(**self.data_to_dict(y_ch, y_ch.guilds))
                              for y_ch in youtube_channels}

        print(self.channels_dict)

        await asyncio.sleep(20)
        self.get_last_video_ntf.start()

    @tasks.loop(seconds=180)
    async def get_last_video_ntf(self):
        for channel_title, c_channel in self.channels_dict.items():
            last_video = await self.youtube.get_last_channel_video(c_channel.id)

            print(last_video, channel_title)
            print((datetime.now() - last_video.published_at).total_seconds())

            delay_s = (datetime.now() - last_video.published_at).total_seconds()

            if c_channel.last_video_id != last_video.id and delay_s < 1200:
                self.bot.loop.create_task(self.notify_about_new_video(channel_title, c_channel.guilds, last_video))
                self.bot.loop.create_task(self.update_channel_last_video(channel_title, last_video))

    async def notify_about_new_video(self, channel_title: str, guilds: list, video: YouTubeVideo):
        for item in guilds:
            guild = self.bot.get_guild(item.guild_id)
            channel = self.bot.get_channel(item.channel_id)

            try:
                roles_ids = {1: '@here', 2: '@everyone'}
                role_mention = roles_ids[item.role_id]
            except KeyError:
                role_mention = guild.get_role(item.role_id).mention if item.role_id else 0

            await channel.send(f'{str(role_mention + ", н") if role_mention else "Н"}'
                               f'а канале **{channel_title}** появилось новое видео!\n{video.video_url}')

    async def update_channel_last_video(self, channel_title: str, new_video: YouTubeVideo):
        channel = await YouTubeChannelDoc.find_one({'_id': self.channels_dict[channel_title].id})
        channel.last_video_id = new_video.id
        await channel.commit()

        self.channels_dict[channel_title].last_video_id = new_video.id

    async def add_to_channel(self, data: dict):
        try:
            if data['guild_id'] in [g_r.guild_id for g_r in self.channels_dict[data['title']].guilds]:
                raise ChannelAlreadyExist
        except KeyError:
            pass

        youtube_channel = await self.youtube.get_channel_by_name(data['title'])
        doc_channel = await YouTubeChannelDoc.find_one({'_id': youtube_channel.channel_id})

        if doc_channel:
            doc_channel.guilds.append(fields.Dict(guild_id=data['guild_id'],
                                                  channel_id=data['channel'],
                                                  role_id=data['role']))
            await doc_channel.commit()

            self.channels_dict[youtube_channel.title].add_guild(guild_id=data['guild_id'],
                                                                role_id=data['role'],
                                                                channel_id=data['channel'])

            return

        await self.add_new_channel(youtube_channel, data)

    async def add_new_channel(self, y_ch: YouTubeChannelRef, data: dict):
        doc_channel = YouTubeChannelDoc(_id=y_ch.channel_id, title=y_ch.title,
                                        last_video_id=y_ch.last_video.id,
                                        guilds=[fields.Dict(guild_id=data['guild_id'],
                                                            channel_id=data['channel'],
                                                            role_id=data['role'])])

        await doc_channel.commit()

        self.channels_dict[y_ch.title] = YouTubeChannel(**self.data_to_dict(doc_channel, doc_channel.guilds))

    async def remove_channel(self, channel_name: str, guild: discord.Guild):
        try:
            item = list(filter(lambda ntp: ntp.guild_id == guild.id, self.channels_dict[channel_name].guilds))[0]
        except KeyError:
            raise ChannelDoesNotExist
        except IndexError:
            raise ChannelDoesNotExist

        self.channels_dict[channel_name].guilds.remove(item)

        doc_channel = await YouTubeChannelDoc.find_one({'title': channel_name})

        if len(self.channels_dict[channel_name].guilds):
            doc_channel.guilds.remove(fields.Dict(guild_id=item.guild_id,
                                                  channel_id=item.channel_id,
                                                  role_id=item.role_id))
            await doc_channel.commit()
            return

        self.channels_dict.pop(channel_name)
        await doc_channel.remove()

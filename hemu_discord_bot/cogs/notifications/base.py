from collections import namedtuple


Guild = namedtuple('Guild', 'guild_id channel_id role_id')


class Channel:
    def __init__(self, **kwargs):
        self.id = kwargs['channel_id']
        self.title = kwargs['title']
        self.guilds = kwargs['guilds']

    def add_guild(self, data: dict):
        self.guilds.append(Guild(guild_id=data['guild_id'], channel_id=data['channel_id'], role_id=data['role_id']))

    def __str__(self):
        return ', '.join([f'{key}: {value}' for key, value in self.__dict__.items()])


class YouTubeChannel(Channel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.last_video_id = kwargs['last_video_id']

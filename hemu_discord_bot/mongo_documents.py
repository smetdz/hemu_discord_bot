from umongo import MotorAsyncIOInstance
from umongo import Document, fields


instance = MotorAsyncIOInstance()


@instance.register
class Guild(Document):
    _id = fields.IntegerField(unique=True)
    title = fields.StrField()
    reactions_status = fields.BooleanField()

    class Meta:
        collection_name = 'guild'


@instance.register
class Tag(Document):
    name = fields.StrField()
    text = fields.StrField()
    guild = fields.ReferenceField(document=Guild)
    user_id = fields.IntegerField()

    class Meta:
        collection_name = 'tag'


@instance.register
class Reaction(Document):
    string = fields.StrField(attribute='_id', unique=True)
    reaction = fields.StrField()
    is_emb = fields.BooleanField()
    guild = fields.ReferenceField(document=Guild)

    class Meta:
        collection_name = 'reaction'


@instance.register
class Channel(Document):
    _id = fields.StrField(unique=True)
    title = fields.StrField()
    guilds = fields.ListField(fields.DictField(guild_id=fields.IntegerField(unique=True),
                                               channel_id=fields.IntegerField(),
                                               role_id=fields.IntegerField()))

    class Meta:
        abstract = True


@instance.register
class TwitchChannel(Channel):
    last_stream_status = fields.BooleanField()

    class Meta:
        collection_name = 'twitch-channel'


@instance.register
class YouTubeChannel(Channel):
    last_video_id = fields.StrField()
    video_count = fields.IntegerField()

    class Meta:
        collection_name = 'youtube-channel'


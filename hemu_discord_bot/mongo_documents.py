import os

from umongo.frameworks import MotorAsyncIOInstance
from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Document, fields


db = AsyncIOMotorClient(os.environ['MONGO_CLIENT'])['discord-hemu-bot']
instance = MotorAsyncIOInstance(db)


@instance.register
class Guild(Document):
    _id = fields.IntegerField(unique=True)
    title = fields.StrField()
    reactions_status = fields.BooleanField()

    class Meta:
        collection_name = 'guild'

@instance.register
class AutoRole(Document):
    _id = fields.IntegerField(unique=True)
    delay = fields.IntegerField()
    active_auto_role = fields.ListField(fields.DictField(
        user_id=fields.IntegerField(),
        date_of_accession=fields.DateTimeField())
    )
    guild = fields.ReferenceField(document=Guild)

    class Meta:
        collection_name = 'autorole'


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
    guilds = fields.ListField(fields.DictField(
        guild_id=fields.IntegerField(unique=True),
        channel_id=fields.IntegerField(),
        role_id=fields.IntegerField())
    )

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


@instance.register
class Poll(Document):
    _id = fields.IntegerField(unique=True)
    creator_id = fields.IntegerField()
    channel_id = fields.IntegerField()
    title = fields.StrField()
    mention_role = fields.StrField()
    duration = fields.IntegerField()
    options_for_voting = fields.ListField(fields.ListField(fields.StrField))

    class Meta:
        collection_name = 'poll'


@instance.register
class Remind(Document):
    _id = fields.IntegerField()
    r_num = fields.IntegerField()
    user_id = fields.IntegerField()
    text = fields.StrField()
    guild = fields.ReferenceField(document=Guild)
    channel_id = fields.IntegerField()
    remind_time = fields.DateTimeField()

    class Meta:
        collection_name = 'remind'

import asyncio
import datetime
import random

import pytz
import discord
from discord.ext import commands
from umongo import fields

from bot import HemuBot
from cogs.utils.poll import Poll
from cogs.utils.list_view import TagsListView
from cogs.utils.checks import role_mentions_check
from cogs.utils import errors
from cogs.utils.utils import get_member, get_role, get_delay, get_utc_datetime
from config import hemu_emoji, poll_options_emoji, base_poll_duration
from mongo_documents import Tag, Guild, Poll as DocumentPoll, Remind


class Tools(commands.Cog):
    def __init__(self, bot: HemuBot):
        self.bot = bot
        self.bot.loop.create_task(self.load_pools_from_bd())
        self.bot.loop.create_task(self.load_reminds())

    @commands.command(name='rand', aliases=('ранд', ))
    async def rand(self, ctx: commands.Context, num1: str, num2: str = '0'):
        try:
            num1, num2 = sorted((int(num1), int(num2)))
        except ValueError:
            await ctx.send(f'Нужны числа {hemu_emoji["angry_hemu"]}')
            return

        rand_num = random.randint(num1, num2)
        await ctx.send(str(rand_num))

    @commands.group(name='remind', aliases=('напоминание', 'напомни', 'нпмн', 'rmnd'))
    async def remind(self, ctx: commands.Context):
        params = ctx.message.content.split()
        sub_commands = ['remove', 'удалить', 'delete', 'del', 'dlt', 'list', 'список', 'lst']
        if params[1] in sub_commands:
            pass
        else:
            await self.add_remind(ctx, params[1], ' '.join(params[2:]))

    async def add_remind(self, ctx: commands.Context, time: str, text: str):
        now = datetime.datetime.utcnow()
        rem_time = None

        try:
            rem_time = get_utc_datetime(time)
            delay = (rem_time - pytz.utc.localize(now)).total_seconds()

            if delay < 0:
                await ctx.send(f'Больше не буду возвращаться в прошлое {hemu_emoji["angry_hemu"]}')
                return
        except ValueError:
            try:
                delay = get_delay(time)
            except errors.InvalidDelay:
                await ctx.send(f'Не могу понять когда тебе напоминать, попробуй еще раз {hemu_emoji["angry_hemu"]}')
                return

        count = await Remind.count_documents({'user_id': ctx.author.id, 'guild': ctx.guild.id})

        remind_id = ctx.message.id

        if not rem_time:
            rem_time = now + datetime.timedelta(seconds=delay)

        remind = Remind(
            _id=remind_id,
            r_num=count + 1,
            user_id=ctx.author.id,
            text=text,
            channel_id=ctx.channel.id,
            guild=fields.Reference(Guild, ctx.guild.id),
            remind_time=rem_time
        )

        await remind.commit()
        await ctx.send(f'Напоминание создано {hemu_emoji["hemu_fun"]}')
        self.bot.loop.create_task(self.process_remind(remind_id, delay))

    async def update_reminds_nums(self, user_id: int, guild_id: int):
        reminds = await self.get_reminds({'user_id': user_id, 'guild': guild_id})
        for i, remind in enumerate(reminds):
            remind.r_num = i + 1
            await remind.commit()

    async def process_remind(self, remind_id: int, delay: int):
        await asyncio.sleep(delay)

        remind = await Remind.find_one({'_id': remind_id})

        user = None
        if remind:
            try:
                channel = self.bot.get_channel(remind.channel_id)
                user = self.bot.get_user(remind.user_id)
                await self.send_remind(channel, user, remind.text)
            except Exception as e:
                print(e)

            await remind.remove()
            if user:
                self.bot.loop.create_task(self.update_reminds_nums(user.id, remind.guild.pk))

    @staticmethod
    async def send_remind(channel: discord.TextChannel, user: discord.User, text: str):
        emb = discord.Embed(title='Напоминаю', description=text, colour=discord.Colour.dark_purple())
        emb.set_footer(icon_url=user.avatar_url, text=f'Запросил {user.name}')
        await channel.send(content=user.mention, embed=emb)

    async def load_reminds(self):
        await asyncio.sleep(30)
        reminds = await self.get_reminds({})

        utc_now = datetime.datetime.utcnow()
        for remind in reminds:
            user = self.bot.get_user(remind.user_id)

            if not user:
                await remind.remove()
                continue

            delay = (remind.remind_time - utc_now).total_seconds()

            if delay < 0:
                delay = 0

            self.bot.loop.create_task(self.process_remind(remind.pk, delay))

    @staticmethod
    async def get_reminds(find_d: dict):
        reminds_ = Remind.find(find_d)
        count = await Remind.count_documents(find_d)
        return await reminds_.to_list(count)

    @remind.command(name='remove', aliases=('удалить', 'delete', 'del', 'dlt'))
    async def remove_remind(self, ctx: commands.Context, r_num: int):
        remind = await Remind.find_one({'user_id': ctx.author.id, 'guild': ctx.guild.id, 'r_num': r_num})

        if remind:
            await remind.remove()
            await ctx.send('Напоминание удалено.')

            self.bot.loop.create_task(self.update_reminds_nums(ctx.author.id, ctx.guild.id))

            return

        await ctx.send(f'Нет напоминания под номером {r_num}')

    @remind.command(name='list', aliases=('список', 'lst'))
    async def show_reminds_list(self, ctx: commands.Context):
        reminds = await self.get_reminds({'user_id': ctx.author.id, 'guild': ctx.guild.id})

        if reminds:
            utc_now = datetime.datetime.utcnow()
            ru_tz = pytz.timezone('Europe/Moscow')
            reminds_str = ''
            for remind in reminds:
                remind_utc_time = pytz.utc.localize(remind.remind_time)
                remind_user_time = remind_utc_time.astimezone(ru_tz)
                reminds_str += f'{remind.r_num} - {remind.text}, ' \
                               f'Напомню: {remind_user_time.strftime("%d.%m.%Y-%H.%M.%S")}\n '
            emb = discord.Embed(title=f'Напоминания пользователя {ctx.author}', colour=discord.Colour.dark_purple(),
                                description=reminds_str[:-1])
            emb.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
            emb.timestamp = utc_now

            await ctx.send(embed=emb)
            return

        await ctx.send(f'Напоминаний нет {hemu_emoji["sad_hemu"]}')

    @commands.command(name='poll', aliases=('голосование',))
    async def poll(self, ctx: commands.Context, poll_title: str, role_name: str, duration_str: str, *emoji_options):
        if role_name in ['нет', 'not', '-']:
            role_mention = ''
        else:
            if ctx.author.guild_permissions.administrator:
                if role_name in ['@everyone', '@here']:
                    role_mention = role_name
                else:
                    try:
                        role_mention = get_role(ctx, role_name).mention
                    except errors.InvalidRole:
                        await ctx.send(f'Роли "{role_name}" нет на сервере, попробуй еще раз.{hemu_emoji["sad_hemu"]}')
                        return
            else:
                await ctx.send('Только пользователи с правами администатора могут пинговать роли. Вызовите команду '
                               'используя в качестве роли нет/not/-.')
                return

        if duration_str in ['нет', 'not', '-']:
            duration = base_poll_duration
        else:
            try:
                duration = get_delay(duration_str)
            except errors.InvalidDelay:
                await ctx.send(f'Не могу понять сколько это "{duration_str}" попробуй еще раз.{hemu_emoji["sad_hemu"]}')
                return

        if not len(emoji_options) % 2:
            option_for_votes = tuple(zip(emoji_options[::2], emoji_options[1::2]))

            poll = Poll(poll_title, option_for_votes, ctx.author, role_mention)
            self.bot.loop.create_task(self.process_poll(poll, duration, option_for_votes, ctx.channel, ctx.message))
            return

        await ctx.send(f'Не получилось, попробуй еще раз {hemu_emoji["sad_hemu"]}')

    @commands.command(name='simplepoll', aliases=('простголос',))
    async def simple_poll(self, ctx: commands.Context, title: str, duration_str: str = None, *options):
        if options:
            options_for_votes = tuple(zip(poll_options_emoji, options))
        else:
            options_for_votes = tuple(zip((hemu_emoji['hemu_fun'], hemu_emoji['sad_hemu']), ('Да', 'Нет')))

        if duration_str in ['нет', 'not', '-', None]:
            duration = base_poll_duration
        else:
            try:
                duration = get_delay(duration_str)
            except errors.InvalidDelay:
                await ctx.send(f'Не могу понять сколько это "{duration_str}" попробуй еще раз.{hemu_emoji["sad_hemu"]}')
                return

        poll = Poll(title, options_for_votes, ctx.author, '')
        self.bot.loop.create_task(self.process_poll(poll, duration, options_for_votes, ctx.channel, ctx.message))

    async def process_poll(self, poll: Poll, duration: int, options: tuple = None, channel: discord.TextChannel = None,
                           user_message: discord.Message = None, new_poll: bool = True):
        try:
            if new_poll:
                message_id = await poll.create_poll(channel)
                self.bot.loop.create_task(self.save_poll_to_bd(poll, duration, options))
            else:
                message_id = await poll.resume_poll()
        except errors.InvalidPoll:
            await channel.send(f'Неправильные эмодзи {hemu_emoji["sad_hemu"]}')
            return
        except Exception as e:
            print(e)
            return

        self.bot.polls[message_id] = poll

        if new_poll:
            await user_message.delete()

        await asyncio.sleep(duration)
        await poll.close_poll()

        self.bot.polls.pop(message_id)

        d_poll = await DocumentPoll.find_one({'_id': message_id})
        await d_poll.remove()

    @staticmethod
    async def save_poll_to_bd(poll: Poll, duration: int, options: tuple):
        poll = DocumentPoll(
            _id=poll.message.id,
            creator_id=poll.creator.id,
            channel_id=poll.message.channel.id,
            title=poll.poll_title,
            mention_role=poll.mention_role,
            duration=duration,
            options_for_voting=[list(opt) for opt in options]
        )

        await poll.commit()

    async def load_pools_from_bd(self):
        d_polls_ = DocumentPoll.find()
        count = await DocumentPoll.count_documents()
        d_polls = await d_polls_.to_list(count)

        await asyncio.sleep(15)

        for d_poll in d_polls:
            channel = self.bot.get_channel(d_poll.channel_id)
            message = await channel.fetch_message(d_poll.pk)
            creator = self.bot.get_user(d_poll.creator_id)
            options_for_voting = tuple(tuple(lst) for lst in d_poll.options_for_voting)
            poll = Poll(d_poll.title, options_for_voting, creator, d_poll.mention_role, message)

            duration = d_poll.duration - int((datetime.datetime.now() - message.created_at).total_seconds())
            self.bot.loop.create_task(self.process_poll(poll, duration, new_poll=False))

    @commands.check(role_mentions_check)
    @commands.group(name='tag', aliases=('тег', ))
    async def tag(self, ctx: commands.Context):
        params = ctx.message.content.split()
        sub_commands = ['create', 'создать', 'add', 'list', 'список', 'lst',
                        'edit', 'изменить', 'delete', 'remove', 'удалить', 'show']

        if params[1] in sub_commands:
            pass
        else:
            await self.return_tag(ctx, ctx.guild.id, ' '.join(params[1:]))

    @commands.check(role_mentions_check)
    @tag.command(name='show')
    async def show(self, ctx: commands.Context, *, tag_name: str):
        await self.return_tag(ctx, ctx.guild.id, tag_name)

    async def return_tag(self, ctx: commands.Context, guild_id: int, tag_name: str):
        tag = await self.find_tag(guild_id, tag_name)

        if tag:
            await ctx.send(f'{tag.text}')
            return

        tag_list = await self.search_tag(guild_id, tag_name)
        await self.return_tag_list(ctx, tag_name, tag_list)

    @staticmethod
    async def return_tag_list(ctx: commands.Context, tag_name: str, tag_list: list):
        if tag_list:
            emb = discord.Embed(title=f'Не могу найти тег {tag_name}, похожее:',
                                colour=discord.Colour.dark_purple(),
                                description='\n'.join(f'**{ind + 1}.** {tag}' for ind, tag in enumerate(tag_list[:20])))
            await ctx.send(embed=emb)
            return

        await ctx.send(f'Тега {tag_name} нет {hemu_emoji["sad_hemu"]}')

    async def search_tag(self, guild_id: int, tag_name: str):
        tags = await self.get_tags(guild_id, all_tags=True)
        s_tag_name = set(tag_name.split())

        return [tag.name for tag in tags if s_tag_name.issubset(set(tag.text.split())) or tag_name in tag.name]

    @staticmethod
    async def get_tags(guild_id: int, user_id: int = None, all_tags: bool = False):
        f_dict = {'guild': guild_id} if all_tags else {'user_id': user_id, 'guild': guild_id}

        tags_ = Tag.find(f_dict)
        count = await Tag.count_documents(f_dict)
        return await tags_.to_list(count)

    @commands.check(role_mentions_check)
    @tag.command(name='create', aliases=('создать', 'add',))
    async def create_tag(self, ctx: commands.Context, tag_name: str, *, tag_text: str):
        try:
            await self.tag_uniq_check(ctx.guild.id, tag_name)
        except errors.TagAlreadyExists:
            await ctx.send('Тег с этим именем уже существует,'
                           ' что бы изменить его содержимое вызовите ```!tag edit [name] [new_text]```')
            return

        ref = fields.Reference
        tag = Tag(name=tag_name, text=tag_text, guild=ref(Guild, ctx.guild.id), user_id=ctx.author.id)
        await tag.commit()

        await ctx.send(f'Тег успешно создан {hemu_emoji["hemu_fun"]}')

    @commands.check(role_mentions_check)
    @tag.command(name='remove', aliases=('delete', 'удалить',))
    async def remove_tag(self, ctx: commands.Context, *, tag_name: str):
        tag = await self.find_tag(ctx.guild.id, tag_name)

        if tag:
            if tag.user_id == ctx.author.id or ctx.author.guild_permissions.manage_messages:
                await tag.remove()
                await ctx.send(f'Тег "{tag_name}" удален')
                return
            await ctx.send(f'Тег не твой {hemu_emoji["angry_hemu"]}')
            return

        tag_list = await self.search_tag(ctx.guild.id, tag_name)
        await self.return_tag_list(ctx, tag_name, tag_list)

    @commands.check(role_mentions_check)
    @tag.command(name='edit', aliases=('изменить',))
    async def edit_tag(self, ctx: commands.Context, tag_name, *, new_tag_text: str):
        tag = await self.find_tag(ctx.guild.id, tag_name)

        if tag:
            if tag.user_id == ctx.author.id or ctx.author.guild_permissions.manage_messages:
                tag.text = new_tag_text
                await tag.commit()
                await ctx.send(f'Содержимое тега "{tag_name}" изменено.')
                return
            await ctx.send(f'Тег не твой {hemu_emoji["angry_hemu"]}')
            return

        tag_list = await self.search_tag(ctx.guild.id, tag_name)
        await self.return_tag_list(ctx, tag_name, tag_list)

    @commands.check(role_mentions_check)
    @tag.command(name='list', aliases=('lst', 'список',))
    async def show_tags(self, ctx: commands.Context, page: str = '1', *, user: str = None):
        try:
            page = int(page)
        except ValueError:
            user = page + ' ' + user if user else page
            page = 1

        if user:
            try:
                member = get_member(ctx, user)
            except errors.InvalidUser:
                await ctx.send(f'Не могу понять, что за пользователь этот твой "{user}",'
                               f' попробуй еще раз. {hemu_emoji["sad_hemu"]}')
                return

            search_d = {'user_id': member.id, 'guild': ctx.guild.id}
            title = f'Теги пользователя {member}:'
        else:
            search_d = {'guild': ctx.guild.id}
            title = f'Теги на сервере {ctx.guild.name}'

        await self.show_tags_list(page, search_d, title, ctx.channel)

    async def show_tags_list(self, page: int, search_d: dict, title: str, channel: discord.TextChannel):
        tags_count = await Tag.count_documents(search_d)

        if not tags_count:
            await channel.send(f'Нет тегов {hemu_emoji["sad_hemu"]}')
            return

        tag_lst_view = TagsListView(title, 15, page, tags_count, search_d, Tag)

        message_id = await tag_lst_view.show(channel)
        self.bot.list_views[message_id] = tag_lst_view

        await asyncio.sleep(120)

        self.bot.list_views.pop(message_id)

    async def tag_uniq_check(self, guild_pk: int, tag_name: str):
        if await self.find_tag(guild_pk, tag_name):
            raise errors.TagAlreadyExists

    @staticmethod
    async def find_tag(guild_pk: int, tag_name: str):
        return await Tag.find_one({'guild': guild_pk, 'name': tag_name})


def setup(bot: HemuBot):
    bot.add_cog(Tools(bot))

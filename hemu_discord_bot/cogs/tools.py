import discord
from discord.ext import commands

from umongo import fields

from bot import HemuBot
from cogs.utils import errors
from cogs.utils.utils import get_member
from config import hemu_emoji
from mongo_documents import Tag, Guild


class Tools(commands.Cog):
    def __init__(self, bot: HemuBot):
        self.bot = bot

    @commands.group(name='tag')
    async def tag(self, ctx: commands.Context):
        pass

    @tag.command(name='show')
    async def show_tag(self, ctx: commands.Context, *, tag_name: str):
        await self.return_tag(ctx, ctx.author.id, ctx.guild.id, tag_name)

    @tag.command(name='usertag')
    async def user_tag(self, ctx: commands.Context, user: str, *, tag_name: str):
        try:
            member = get_member(ctx, user)
            await self.return_tag(ctx, member.id, ctx.guild.id, tag_name)
        except errors.InvalidUser:
            await ctx.send(f'Не могу понять, что за пользователь этот твой "{user}",'
                           f' попробуй еще раз. {hemu_emoji["sad_hemu"]}')

    async def return_tag(self, ctx: commands.Context, user_id: int, guild_id: int, tag_name: str):
        tag = await self.find_tag(user_id, guild_id, tag_name)

        if tag:
            await ctx.send(f'{tag.text}')
            return

        tag_list = await self.search_tag(user_id, guild_id, tag_name)
        await self.return_tag_list(ctx, tag_name, tag_list)

    @staticmethod
    async def return_tag_list(ctx: commands.Context, tag_name: str, tag_list: list):
        if tag_list:
            emb = discord.Embed(title=f'Не могу найти тег {tag_name}, похожее:',
                                colour=discord.Colour.dark_purple(),
                                description=', '.join(tag_list))
            await ctx.send(embed=emb)
            return

        await ctx.send(f'Тега {tag_name} нет {hemu_emoji["sad_hemu"]}')

    async def search_tag(self, user_id: int, guild_id: int, tag_name: str):
        tags = await self.get_tags(user_id, guild_id)
        s_tag_name = set(tag_name.split())

        return [tag.name for tag in tags if s_tag_name.issubset(set(tag.text.split())) or tag_name in tag.name]

    @staticmethod
    async def get_tags(user_id: int, guild_id: int, all_tags: bool = False):
        f_dict = {'guild': guild_id} if all_tags else {'user_id': user_id, 'guild': guild_id}

        tags_ = Tag.find(f_dict)
        count = await Tag.count_documents({'user_id': user_id, 'guild': guild_id})
        return await tags_.to_list(count)

    @tag.command(name='create', aliases=('создать', 'add',))
    async def create_tag(self, ctx: commands.Context, tag_name: str, *, tag_text: str):
        try:
            await self.tag_uniq_check(ctx.author.id, ctx.guild.id, tag_name)
        except errors.TagAlreadyExists:
            await ctx.send('Тег с этим именем уже существует,'
                           ' что бы изменить его содержимое вызовите ```!tag edit [name] [new_text]```')
            return

        ref = fields.Reference
        tag = Tag(name=tag_name, text=tag_text, guild=ref(Guild, ctx.guild.id), user_id=ctx.author.id)
        await tag.commit()

        await ctx.send(f'Тег успешно создан {hemu_emoji["hemu_fun"]}')

    @tag.command(name='remove', aliases=('delete', 'del', 'dlt', 'удалить',))
    async def remove_tag(self, ctx: commands.Context, tag_name: str):
        tag = await self.find_tag(ctx.author.id, ctx.guild.id, tag_name)

        if tag:
            await tag.remove()
            await ctx.send(f'Тег "{tag_name}" удален')
            return

        tag_list = await self.search_tag(ctx.author.id, ctx.guild.id, tag_name)
        await self.return_tag_list(ctx, tag_name, tag_list)

    @tag.command(name='edit', aliases=('изменить',))
    async def edit_tag(self, ctx: commands.Context, tag_name, *, new_tag_text: str):
        tag = await self.find_tag(ctx.author.id, ctx.guild.id, tag_name)

        if tag:
            tag.text = new_tag_text
            await tag.commit()
            await ctx.send(f'Содержимое тега {tag_name} изменено.')
            return

        tag_list = await self.search_tag(ctx.author.id, ctx.guild.id, tag_name)
        await self.return_tag_list(ctx, tag_name, tag_list)

    @tag.command(name='list', aliases=('lst', 'список',))
    async def show_tags_list(self, ctx: commands.Context):
        tags = await self.get_tags(ctx.author.id, ctx.guild.id)

        if tags:
            emb = discord.Embed(title=f'Теги пользователя {ctx.author}:',
                                colour=discord.Colour.dark_purple(),
                                description=', '.join([f'{tag.name}' for tag in tags]))
            await ctx.send(embed=emb)
            return

        await ctx.send(f'Нет тегов {hemu_emoji["sad_hemu"]}')

    @tag.command(name='all', aliases=('все',))
    @commands.has_permissions(administrator=True)
    async def show_all_tags(self, ctx: commands.Context):
        tags = await self.get_tags(ctx.author.id, ctx.guild.id, True)

        if tags:
            emb = discord.Embed(title=f'Теги на сервере {ctx.guild}:',
                                colour=discord.Colour.dark_purple(),
                                description='\n'.join([f'{ind + 1}. Тег: {tag.name},'
                                                       f' пользователь: {self.bot.get_user(tag.user_id)}'
                                                       for ind, tag in enumerate(tags)]))
            await ctx.send(embed=emb)
            return

        await ctx.send(f'На сервере нет тегов {hemu_emoji["sad_hemu"]}')

    async def tag_uniq_check(self, user_id: int, guild_pk: int, tag_name: str):
        if await self.find_tag(user_id, guild_pk, tag_name):
            raise errors.TagAlreadyExists

    @staticmethod
    async def find_tag(user_id: int, guild_pk: int, tag_name: str):
        return await Tag.find_one({'user_id': user_id, 'guild': guild_pk, 'name': tag_name})


def setup(bot: HemuBot):
    bot.add_cog(Tools(bot))
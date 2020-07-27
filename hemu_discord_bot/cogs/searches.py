import discord
from discord.ext import commands

from bot import HemuBot
from config import hemu_emoji
from cogs.notifications.youtube_ntf import YouTubeNotifier
from cogs.services.openweather import OpenWeatherRef
from cogs.services.youtube import YouTubeRef
from cogs.utils.errors import VideoDoesNotExist, ChannelDoesNotExist
from cogs.utils.utils import get_role, get_text_channel
from cogs.utils import errors
from cogs.utils import embeds


class Searches(commands.Cog):
    def __init__(self, bot: HemuBot):
        self.bot = bot
        self.youtube_notifier = YouTubeNotifier(self.bot)

    @commands.group(name='youtube', invoke_without_command=True)
    async def youtube(self, ctx: commands.Context):
        s = ''
        for key, item in self.youtube_notifier.channels_dict.items():
            s += f'{key} : {item}\n'
        await ctx.send(s)

    @youtube.command(name='list', aliases=('lst', 'show'))
    async def show_ntf_channels_list(self, ctx: commands.Context):
        youtube_channels = list(filter(lambda ch: ctx.guild.id in [g.guild_id for g in ch.guilds],
                                       self.youtube_notifier.channels_dict.values()))

        if youtube_channels:
            emb = discord.Embed(title=f'Ютуб каналы сервера {ctx.guild.name}', colour=discord.Colour.dark_purple())

            for channel in youtube_channels:
                guild_inf = list(filter(lambda g: ctx.guild.id == g.guild_id, channel.guilds))[0]

                txt_channel = self.bot.get_channel(guild_inf.channel_id)

                try:
                    roles_ids = {1: '@here', 2: '@everyone'}
                    role_mention = roles_ids[guild_inf.role_id] if guild_inf.role_id else '-'
                except KeyError:
                    role_mention = ctx.guild.get_role(guild_inf.role_id).mention

                val = f'текстовый канал: {txt_channel.mention}, роль: {role_mention}'

                emb.add_field(inline=False, name=channel.title, value=val)

            emb.set_author(icon_url=self.bot.user.avatar_url, name='Hemu')
            emb.set_footer(text=f'Запрошено {ctx.author.name}')

            await ctx.send(embed=emb)
            return

        await ctx.send(f'Нет ютуб каналов.{hemu_emoji["sad_hemu"]}')

    @youtube.command(name='add', alisases=('добавить', ))
    @commands.has_permissions(administrator=True)
    async def add_youtube_channel(self, ctx: commands.Context, channel_title: str,
                                  ntf_txt_channel: str, role_name: str = None):
        print(channel_title, ntf_txt_channel, role_name)
        data = await self.prepare_ntf_data(ctx, channel_title, ntf_txt_channel, role_name)

        if not data:
            return

        try:
            await self.youtube_notifier.add_to_channel(data)
            await ctx.send(f'Канал успешно сохранен.{hemu_emoji["hemu_fun"]}')
        except Exception as e:
            print(e.args, e)
            await ctx.send(f'Произошла ошибка при сохранении.{hemu_emoji["sad_hemu"]}')

    @youtube.command(name='remove', aliases=('del', 'delete'))
    @commands.has_permissions(administrator=True)
    async def remove_youtube_channel(self, ctx: commands.Context, *, channel_name: str):
        try:
            await self.youtube_notifier.remove_channel(channel_name, ctx.guild)
            await ctx.send(f'Канал "**{channel_name}**" удален.')
        except ChannelDoesNotExist:
            await ctx.send(f'Канала "**{channel_name}**" нет.')

    @staticmethod
    async def prepare_ntf_data(ctx: commands.Context, channel_title: str, ntf_txt_channel: str, role_name: str):
        if role_name:
            roles_ids = {'@here': 1, '@everyone': 2}

            try:
                role_id = roles_ids[role_name]
            except KeyError:
                try:
                    role_id = get_role(ctx, role_name).id
                except errors.InvalidRole:
                    await ctx.send(f'Роли "{role_name}" нет на сервере, попробуй еще раз.{hemu_emoji["sad_hemu"]}')
                    return
        else:
            role_id = 0

        try:
            channel_id = get_text_channel(ctx, ntf_txt_channel).id
        except errors.InvalidTextChannel:
            await ctx.send(f'Текстового канала "{ntf_txt_channel}" нет на сервере,'
                           f' попробуй еще раз.{hemu_emoji["sad_hemu"]}')
            return

        return {
            'guild_id': ctx.guild.id,
            'title': channel_title,
            'role': role_id,
            'channel': channel_id,
        }

    @youtube.command(name='search', aliases=('найти',))
    async def search_youtube_video(self, ctx: commands.Context, *, video_title: str):
        try:
            video = await YouTubeRef().get_video(video_title)
        except VideoDoesNotExist:
            await ctx.send(f'Не могу найти видео "{video_title}", попробуй еще раз.{hemu_emoji["sad_hemu"]}')
            return

        await ctx.send(video.video_url)

    @commands.command(name='погода', aliases=('w', 'weather'))
    async def weather(self, ctx: commands.Context, *, city: str):
        weather = await OpenWeatherRef().get_weather(city)
        if weather:
            print(f'weather: {weather}')
            weather_emb = embeds.create_weather_emb(city, weather)

            await ctx.send(embed=weather_emb)
            return

        await ctx.send(f'Не знаю такого города как "**{city}**", попробуй еще раз.{hemu_emoji["sad_hemu"]}')


def setup(bot: HemuBot):
    bot.add_cog(Searches(bot))

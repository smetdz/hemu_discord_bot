from typing import Union

import discord
from discord.ext import commands

from cogs.services.shikimori import ShikimoriRef, Anime, Manga, Ranobe
from cogs.utils.embeds import create_title_emb


class TitleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='anime', aliases=('аниме',))
    async def anime_eng(self, ctx: commands.Context, *, anime_name: str):
        anime = await ShikimoriRef().get_title(anime_name.lower(), 'anime')
        print(anime)

        if anime:
            await self.return_title(ctx, 'anime', anime)
            return

        await ctx.send(f'Не могу найти аниме "**{anime_name}**". Попробуй еще раз.')

    @commands.command(name='manga', aliases=('манга',))
    async def manga_eng(self, ctx: commands.Context, *, manga_name: str):
        manga = await ShikimoriRef().get_title(manga_name.lower(), 'manga')
        print(manga)

        if manga:
            await self.return_title(ctx, 'manga', manga)
            return

        await ctx.send(f'Не могу найти мангу "**{manga_name}**". Попробуй еще раз.')

    @commands.command(name='ranobe', aliases=('ранобэ',))
    async def ranobe_eng(self, ctx: commands.Context, *, ranobe_name: str):
        ranobe = await ShikimoriRef().get_title(ranobe_name.lower(), 'ranobe')
        print(ranobe)

        if ranobe:
            await self.return_title(ctx, 'ranobe', ranobe)
            return

        await ctx.send(f'Не могу найти ранобе "**{ranobe_name}**". Попробуй еще раз.')

    @staticmethod
    async def return_title(ctx: commands.Context, title_type: str,
                           title: Union[Anime, Manga, Ranobe, list]):
        message_type = {
            'anime': 'Найденные аниме',
            'manga': 'Найденная манга',
            'ranobe': 'Найденные ранобе',
        }

        if isinstance(title, list):
            titles_list = '\n'.join(title)
            emb = discord.Embed(title=f'{message_type[title_type]}:', colour=discord.Color.dark_purple(),
                                description=f'{titles_list}\n\n'
                                            f'Вызови команду и напиши название полностью.')
            await ctx.send(embed=emb)
            return
        else:
            title_emb = create_title_emb(title)
            await ctx.send(embed=title_emb)
            return


def setup(bot: commands.Bot):
    bot.add_cog(TitleCog(bot))

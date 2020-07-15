from typing import Union

import discord
from discord.ext import commands

from cogs.services.shikimori import ShikimoriRef, Anime, Manga, Ranobe, Character
from cogs.utils.embeds import create_title_emb, create_char_emb


class TitleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='anime', aliases=('аниме',))
    async def anime(self, ctx: commands.Context, *, anime_name: str):
        anime = await ShikimoriRef().get_info(anime_name.lower(), 'anime')
        print(anime)

        if anime:
            await self.return_info(ctx, 'anime', anime)
            return

        await ctx.send(f'Не могу найти аниме "**{anime_name}**". Попробуй еще раз.')

    @commands.command(name='manga', aliases=('манга',))
    async def manga(self, ctx: commands.Context, *, manga_name: str):
        manga = await ShikimoriRef().get_info(manga_name.lower(), 'manga')
        print(manga)

        if manga:
            await self.return_info(ctx, 'manga', manga)
            return

        await ctx.send(f'Не могу найти мангу "**{manga_name}**". Попробуй еще раз.')

    @commands.command(name='ranobe', aliases=('ранобэ',))
    async def ranobe(self, ctx: commands.Context, *, ranobe_name: str):
        ranobe = await ShikimoriRef().get_info(ranobe_name.lower(), 'ranobe')
        print(ranobe)

        if ranobe:
            await self.return_info(ctx, 'ranobe', ranobe)
            return

        await ctx.send(f'Не могу найти ранобе "**{ranobe_name}**". Попробуй еще раз.')

    @commands.command(name='character', aliases=('персонаж',))
    async def character(self, ctx: commands.Context, *, char_name: str):
        character = await ShikimoriRef().get_info(char_name.lower(), 'character')
        print(character)

        if character:
            await self.return_info(ctx, 'character', character)
            return

        await ctx.send(f'Не могу найти персонажа "**{char_name}**". Попробуй еще раз.')

    @staticmethod
    async def return_info(ctx: commands.Context, info_type: str,
                          info: Union[Anime, Manga, Ranobe, Character, list]):
        message_type = {
            'anime': 'Найденные аниме',
            'manga': 'Найденная манга',
            'ranobe': 'Найденные ранобе',
            'character': 'Найденные персонажи'
        }

        if isinstance(info, list):
            items_list = '\n'.join(info)
            emb = discord.Embed(title=f'{message_type[info_type]}:', colour=discord.Color.dark_purple(),
                                description=f'{items_list}\n\n'
                                            f'Вызови команду и напиши название полностью.')
            await ctx.send(embed=emb)
            return

        if info_type == 'character':
            info_emb = create_char_emb(info)
        else:
            info_emb = create_title_emb(info)

        await ctx.send(embed=info_emb)
        return


def setup(bot: commands.Bot):
    bot.add_cog(TitleCog(bot))

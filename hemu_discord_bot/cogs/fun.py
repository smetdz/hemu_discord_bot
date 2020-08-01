import discord
from discord.ext import commands
from discord.utils import get

import config
from cogs.utils.utils import get_member
from cogs.utils import errors
from config import hemu_emoji


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='avatar', aliases=('аватар',))
    async def avatar(self, ctx: commands.Context, *, member: str = None):
        if member:
            try:
                user = get_member(ctx, member)
            except errors.InvalidUser:
                await ctx.send(f'Не могу понять, что за пользователь этот твой "{member}",'
                               f' попробуй еще раз.{hemu_emoji["sad_hemu"]}')
                return
        else:
            user = ctx.author

        icon_emb = discord.Embed(title=f'Аватар {user.name}', colour=discord.Color.dark_purple())
        icon_emb.set_image(url=user.avatar_url)

        await ctx.send(embed=icon_emb)

    @commands.command(name='kyuubey', aliases=('кубей',))
    async def kubey(self, ctx: commands.Context):
        kubey_emb = discord.Embed(title=f'Уйди!', colour=discord.Color.dark_purple())
        kubey_emb.set_image(url=config.img_urls['kubey'])

        await ctx.send(embed=kubey_emb)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

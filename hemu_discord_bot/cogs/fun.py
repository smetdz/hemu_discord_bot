import discord
from discord.ext import commands

import config


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='аватар')
    async def avatar(self, ctx: commands.Context, member=None):
        if member:
            try:
                user = list(ctx.message.mentions)[0]
            except IndexError:
                await ctx.send(f'Не могу понять, что за пользователь этот твой "{member}", попробуй еще раз')
                return
        else:
            user = ctx.author

        icon_emb = discord.Embed(title=f'Аватар {user.name}', colour=discord.Color.dark_purple())
        icon_emb.set_image(url=user.avatar_url)

        await ctx.send(embed=icon_emb)

    @commands.command(name='кубей')
    async def kubey(self, ctx: commands.Context):
        kubey_emb = discord.Embed(title=f'Уйди!', colour=discord.Color.dark_purple())
        kubey_emb.set_image(url=config.img_urls['kubey'])

        await ctx.send(embed=kubey_emb)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

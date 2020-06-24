import discord
from discord.ext import commands

import config
from utils import not_admin_answer


commands_list = []


def list_decorator(func):
    commands_list.append(func)


@list_decorator
@commands.command(name='аватар')
async def avatar(ctx: commands.Context, member=None):
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


@list_decorator
@commands.command(name='кубей')
async def kubey(ctx: commands.Context):
    kubey_emb = discord.Embed(title=f'Уйди!', colour=discord.Color.dark_purple())
    kubey_emb.set_image(url=config.img_urls['kubey'])

    await ctx.send(embed=kubey_emb)


@list_decorator
@commands.command(name='усни')
async def switch_of(ctx: commands.Context):
    if ctx.author.id == config.CREATOR_ID:
        sleep_emb = discord.Embed(title='Засыпаю...')
        sleep_emb.set_image(url=config.img_urls['sleep'])

        await ctx.send(embed=sleep_emb)
        exit()

    await not_admin_answer(ctx)



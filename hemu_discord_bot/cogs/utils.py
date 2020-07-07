import discord
from discord.ext import commands
from discord.utils import get

import config


async def reactions(bot: commands.Bot, message: discord.Message):
    bot_role = get(message.guild.roles, name='Hemu')

    if bot.user in message.mentions or bot_role in message.role_mentions:
        await message.channel.send(config.emoji_dict['angry_hemu'])

    text = str(message.content).lower()

    if 'киригири' in text:
        await message.channel.send(config.emoji_dict['kirigiri'])

    if 'падла' in text or 'гнус' in text:
        emb = discord.Embed(title='', colour=discord.Color.dark_purple())
        emb.set_image(url=config.img_urls['sayaka'])
        await message.channel.send(f'{message.content}', embed=emb)

    if 'ты такие вещи не говори' in text:
        emb = discord.Embed(title='', colour=discord.Color.dark_purple())
        emb.set_image(url=config.img_urls['things_fun'])
        await message.channel.send(embed=emb)
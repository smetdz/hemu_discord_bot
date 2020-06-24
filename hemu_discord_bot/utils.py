import discord
from discord.utils import get

import config


def create_greeting(member: discord.Member, guild: discord.Guild) -> discord.Embed:
    ch_rules = get(member.guild.text_channels, id=config.channels['rules_ch'])
    ch_info = get(member.guild.text_channels, id=config.channels['info_ch'])

    template = {
        'title': f'Привет, {member.name}!\n',
        'description': f'Добро пожаловать в мир истинных мужчин и девочек волшебниц, {member.mention}!\n'
                       f'Прежде чем начать общение,\n предлагаю тебе пройти в канал {ch_rules.mention},\n'
                       f'чтобы изучить условия нашего контракта.\n'
                       f'А также посетить канал {ch_info.mention} -\n'
                       f'это позволит тебе легче освоиться на нашем сервере!\n'
                       f'И напоследок хочу пожелать тебе приятного общения!~',
    }

    greeting_emb = discord.Embed(title=template['title'], description=template['description'],
                                 colour=discord.Color.dark_purple())
    greeting_emb.set_footer(text=guild.name, icon_url=guild.icon_url)
    greeting_emb.set_image(url=config.img_urls['member_join'])
    greeting_emb.set_thumbnail(url=member.avatar_url)

    return greeting_emb

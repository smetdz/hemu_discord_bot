import discord

import config


def create_greeting(member: discord.Member, guild: discord.Guild) -> discord.Embed:
    ch_rules = list(filter(lambda ch: ch.name == '🗿правила', guild.text_channels))[0]
    ch_info = list(filter(lambda ch: ch.name == '📑инфо', guild.text_channels))[0]

    template = {
        'title': f'Привет, {member.name}!\n',
        'description': f'Добро пожаловать в мир истинных мужчин и девочек волшебниц, {member.mention}!\n'
                       f'Прежде чем начать общение,\n предлагаю тебе пройти в канал {ch_rules.mention},\n'
                       f'чтобы изучить условия нашего контракта.\n'
                       f'А также посетить канал {ch_info.mention} -\n'
                       f'это позволит тебе легче освоиться на нашем сервере!\n'
                       f'И напоследок хочу пожелать тебе приятного общения!~',
        'image_url': 'https://cdn.discordapp.com/attachments/724400545313587271/724585137731403786/3a5752e99cb6915a1f3b8bad68b3582a.gif'

    }

    greeting_emb = discord.Embed(title=template['title'], description=template['description'],
                                 colour=discord.Color.dark_purple())

    greeting_emb.set_footer(text=guild.name, icon_url=guild.icon_url)
    greeting_emb.set_image(url=template['image_url'])
    greeting_emb.set_thumbnail(url=member.avatar_url)

    return greeting_emb

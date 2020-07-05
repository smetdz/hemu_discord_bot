import discord
from discord.ext import commands
from discord.utils import get

import config


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild, command: bool = False, chanel: discord.TextChannel = None):
        if not command:
            print(f'Join to server {guild.name}')

        if not chanel:
            chanel = get(guild.text_channels, id=config.channels['greeting_ch'])

        greeting_emb = discord.Embed(colour=discord.Color.dark_purple())
        greeting_emb.set_image(url=config.img_urls['server_join'])

        await chanel.send('**Всем привет, меня зовут Hemu-chan, надеюсь мы подружимся!~~**', embed=greeting_emb)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print(f'New member {member.name}')
        try:
            chanel = get(member.guild.text_channels, id=config.channels['greeting_ch'])
        except KeyError:
            chanel = member.guild.text_channels[0]

        guild = member.guild
        emb_greeting = self.create_greeting(member, guild)

        await chanel.send(embed=emb_greeting)

    @commands.command(name='представься')
    async def introduce(self, ctx: commands.Context):
        await self.on_guild_join(ctx.guild, True, ctx.channel)

    @staticmethod
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


def setup(bot: commands.Bot):
    bot.add_cog(Welcome(bot))

import asyncio
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get

import config
from mongo_documents import AutoRole, fields


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.load_active_auto_roles())

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

        chanel = get(member.guild.text_channels, id=config.channels['greeting_ch'])

        if not chanel:
            chanel = list(member.guild.text_channels)[0]

        guild = member.guild
        emb_greeting = self.create_greeting(member, guild)

        await chanel.send(f'{member.mention}', embed=emb_greeting)

        await self.set_auto_roles(member)

    @commands.command(name='представься')
    async def introduce(self, ctx: commands.Context):
        await self.on_guild_join(ctx.guild, True, ctx.channel)

    @staticmethod
    async def get_auto_roles(find_c: dict = None):
        if not find_c:
            find_c = {}

        auto_roles = AutoRole.find(find_c)
        count = await AutoRole.count_documents(find_c)
        return await auto_roles.to_list(count)

    async def load_active_auto_roles(self):
        await asyncio.sleep(30)

        auto_roles = await self.get_auto_roles()
        for role in auto_roles:
            guild = self.bot.get_guild(role.guild.pk)
            g_role = guild.get_role(role.pk)
            for item in role.active_auto_role:
                member = guild.get_member(item['user_id'])

                if not member:
                    role.active_auto_role.remove(item)
                    await role.commit()
                    continue

                delay = int((datetime.now() - item['date_of_accession']).total_seconds())

                if delay >= role.delay:
                    delay = 1
                else:
                    delay = role.delay - delay

                self.bot.loop.create_task(self.set_role(member, g_role, delay))

    async def set_auto_roles(self, member: discord.Member):
        auto_roles = await self.get_auto_roles({'guild': member.guild.id})

        for role in auto_roles:
            role.active_auto_role.append({'user_id': member.id, 'date_of_accession': datetime.now()})
            await role.commit()
            self.bot.loop.create_task(self.set_role(member, member.guild.get_role(role.pk), role.delay))

    @staticmethod
    async def set_role(member: discord.Member, role: discord.Role, delay: int):
        await asyncio.sleep(delay)

        auto_role = await AutoRole.find_one({'_id': role.id})
        user_r = list(filter(lambda r: r['user_id'] == member.id, auto_role.active_auto_role))[0]
        auto_role.active_auto_role.remove(user_r)

        await member.add_roles(role)

        await auto_role.commit()

    @staticmethod
    def create_greeting(member: discord.Member, guild: discord.Guild) -> discord.Embed:
        ch_rules = get(member.guild.text_channels, id=config.channels['rules_ch'])
        ch_info = get(member.guild.text_channels, id=config.channels['info_ch'])

        template = {
            'title': f'Привет, {member.name}!\n',
            'description': f'Добро пожаловать в мир истинных мужчин и девочек волшебниц, {member.mention}!\n'
                           f'Прежде чем начать общение,\n предлагаю тебе пройти в канал '
                           f'{ch_rules.mention if ch_rules else "с правилами"},\n'
                           f'чтобы изучить условия нашего контракта.\n'
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

import discord
from discord.ext import commands
from discord.utils import get

from mongo_documents import AutoRole, fields, Guild
from config import hemu_emoji
from cogs.utils import errors
from cogs.utils.utils import get_role, get_delay
from bot import HemuBot


class Roles(commands.Cog):
    def __init__(self, bot: HemuBot):
        self.bot = bot

    @commands.group(name='autorole')
    async def auto_role(self, ctx: commands.Context):
        pass

    @auto_role.command(name='add')
    @commands.has_permissions(administrator=True)
    async def add_auto_role(self, ctx: commands.Context, role_name: str, delay_str: str = None):
        try:
            role = get_role(ctx, role_name)
        except errors.InvalidRole:
            await ctx.send(f'Роли "{role_name}" нет на сервере, попробуй еще раз.{hemu_emoji["sad_hemu"]}')
            return

        if delay_str:
            try:
                delay = get_delay(delay_str)
            except errors.InvalidDelay:
                await ctx.send(f'Не могу понять сколько это "{delay_str}" попробуй еще раз.{hemu_emoji["sad_hemu"]}')
                return
        else:
            delay = 1

        auto_role = AutoRole(_id=role.id, delay=delay, active_auto_role=[], guild=fields.Reference(Guild, ctx.guild.id))

        try:
            await auto_role.commit()
            await ctx.send('Автороль успешно создана.')
        except Exception as e:
            await ctx.send(f'Произошла ошибка, попробуйте еще раз.{hemu_emoji["sad_hemu"]}')
            print(e)

    @auto_role.command(name='remove')
    @commands.has_permissions(administrator=True)
    async def remove_auto_role(self, ctx: commands.Context, role_name: str):
        try:
            role = get_role(ctx, role_name)
        except errors.InvalidRole:
            await ctx.send(f'Роли "{role_name}" нет на сервере, попробуй еще раз.{hemu_emoji["sad_hemu"]}')
            return

        auto_role = await AutoRole.find_one({'_id': role.id})

        if auto_role:
            await auto_role.remove()
            await ctx.send(f'Автороль "{role_name}" удалена.{hemu_emoji["sad_hemu"]}')
            return

        await ctx.send(f'Такой автороли "{role_name}" нет на сервере.{hemu_emoji["sad_hemu"]}')

    @auto_role.command(name='list')
    @commands.has_permissions(administrator=True)
    async def auto_role_list(self, ctx: commands.Context):
        auto_roles_ = AutoRole.find({'guild': ctx.guild.id})
        count = await AutoRole.count_documents({'guild': ctx.guild.id})
        auto_roles = await auto_roles_.to_list(count)

        if auto_roles:
            description = '\n'.join([f'{i + 1}. Роль: {ctx.guild.get_role(r.pk)},'
                                     f' время по истечению которого дается роль: {r.delay}с'
                                     for i, r in enumerate(auto_roles)])

            emb = discord.Embed(title=f'Aвтороли на сервере {ctx.guild.name}:',
                                colour=discord.Colour.dark_purple(),
                                description=description)

            await ctx.send(embed=emb)
            return

        await ctx.send('На сервере отсутствуют автороли.')

    @commands.command(name='роль', aliases=('role',))
    async def role_info(self, ctx: commands.Context, *, role_name: str = None):
        if role_name:
            role = get(ctx.guild.roles, mention=role_name)
            if not role:
                role = get(ctx.guild.roles, name=role_name)

                if not role:
                    await ctx.send(f'Роли "{role_name}" нет на сервере, попробуй еще раз. {hemu_emoji["sad_hemu"]}')
                    return

            role_emb = discord.Embed(title=f'Пользователи с ролью {role.name}', colour=role.colour,
                                     description=', '.join([member.name for member in role.members]))

            await ctx.send(embed=role_emb)


def setup(bot: HemuBot):
    bot.add_cog(Roles(bot))

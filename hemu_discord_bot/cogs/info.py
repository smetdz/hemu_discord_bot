import discord
from discord.ext import commands
from discord.utils import get


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='роль')
    async def role_info(self, ctx: commands.Context, *, role_name: str = None):
        if role_name:
            try:
                role = list(ctx.message.role_mentions)[0]
            except IndexError:
                role = get(ctx.guild.roles, name=role_name)

                if not role:
                    await ctx.send(f'Роли "{role}" нет на сервере, попробуй еще раз.')
                    return

            role_emb = discord.Embed(title=f'Пользователи с ролью {role.name}', colour=role.colour,
                                     description=', '.join([member.name for member in role.members]))

            await ctx.send(embed=role_emb)


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))

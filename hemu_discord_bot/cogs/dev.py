import inspect

import discord
from discord.ext import commands


class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx: commands.Context, *, code: str):
        print(code)

        variables = {
            'ctx': ctx,
        }

        if 'pathlib' in code:
            import pathlib
            variables['pathlib'] = pathlib

        res = eval(code, variables)
        print(res)

        if inspect.isawaitable(res):
            await res
        else:
            await ctx.send(res)


def setup(bot: commands.Bot):
    bot.add_cog(Dev(bot))

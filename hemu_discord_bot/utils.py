import discord
from discord.utils import get
from discord.ext import commands

import config


async def not_admin_answer(ctx: commands.Context):
    angry_enb = discord.Embed(title='Прав маловато, не буду слушаться.')
    angry_enb.set_image(url=config.img_urls['angry'])

    await ctx.send(embed=angry_enb)

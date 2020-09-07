from discord.ext import commands

from config import hemu_emoji


async def role_mentions_check(ctx: commands.Context):
    text = ctx.message.content
    if any([ctx.message.role_mentions, '@everyone' in text, '@here' in text]):
        await ctx.send(f'Пинговать роль не буду {hemu_emoji["angry_hemu"]}')
        return False

    return True

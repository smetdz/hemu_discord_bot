from discord.utils import get
from discord.ext import commands

from cogs.utils import errors


def get_role(ctx: commands.Context, role_name: str):
    if role_name in ['@here', '@every']:
        return role_name

    role = get(ctx.guild.roles, mention=role_name)
    if not role:
        role = get(ctx.guild.roles, name=role_name)

        if not role:
            raise errors.InvalidRole

    return role


def get_text_channel(ctx: commands.Context, channel_name: str):
    txt_channel = get(ctx.guild.text_channels, mention=channel_name)
    if not txt_channel:
        txt_channel = get(ctx.guild.text_channels, name=channel_name)

        if not txt_channel:
            raise errors.InvalidTextChannel

    return txt_channel

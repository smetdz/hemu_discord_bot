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


def get_member(ctx: commands.Context, member: str):
    try:
        user = list(ctx.message.mentions)[0]
        return user
    except IndexError:
        user = None
        fields = ['name', 'display_name', 'id']

        for field in fields:
            if field == 'id':
                try:
                    user = get(ctx.guild.members, **{field: int(member)})
                except ValueError:
                    pass
            else:
                user = get(ctx.guild.members, **{field: member})

            if user:
                return user

    raise errors.InvalidUser

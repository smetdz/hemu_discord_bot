import random

import discord
from discord.ext import commands

import config
from cogs.utils.utils import get_member
from cogs.utils import errors
from cogs.services import tenor
from config import hemu_emoji, hemu_hugs_gifs


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tenor_ref = tenor.TenorRef()

        self.hug_gifs = None
        self.kiss_gifs = None
        self.slap_gifs = None

        self.bot.loop.create_task(self.load_gifs())

    async def load_gifs(self):
        self.hug_gifs = await self.tenor_ref.get_gifs_list('anime hug')
        self.kiss_gifs = await self.tenor_ref.get_gifs_list('anime kiss')
        self.slap_gifs = await self.tenor_ref.get_gifs_list('anime slap')

    @commands.command(name='avatar', aliases=('аватар',))
    async def avatar(self, ctx: commands.Context, *, member: str = None):
        if member:
            user = await self.user_check_and_return(ctx, member)
            if not user:
                return
        else:
            user = ctx.author

        icon_emb = discord.Embed(title=f'Аватар {user.name}', colour=discord.Color.dark_purple())
        icon_emb.set_image(url=user.avatar_url)

        await ctx.send(embed=icon_emb)

    @staticmethod
    async def user_check_and_return(ctx: commands.Context, user: str):
        try:
            return get_member(ctx, user)
        except errors.InvalidUser:
            await ctx.send(f'Не могу понять, что за пользователь этот твой "{user}",'
                           f' попробуй еще раз.{hemu_emoji["sad_hemu"]}')

    def choose_description(self, author: discord.User, user: discord.User, act: str):
        description_vars = self.get_description_vars(user.display_name, author.display_name, act)
        if user.id == self.bot.user.id:
            return description_vars[0]
        elif user.id == author.id:
            return description_vars[1]
        else:
            return description_vars[2]

    @staticmethod
    def get_description_vars(user_display_name: str, author_display_name: str, act: str):
        emoji1 = hemu_emoji['hemu_what'] if act == 'бьет' else hemu_emoji['hemu_love']
        emoji2 = hemu_emoji['sad_hemu'] if act == 'бьет' else hemu_emoji['surprised_hemu']
        emoji3 = hemu_emoji['sad_hemu'] if act == 'бьет' else hemu_emoji['embarrassed_hemu']

        description_vars = [
            f'**{author_display_name}** {act} меня {emoji1}',
            f'**{user_display_name}** {act} себя {emoji2}',
            f'**{author_display_name}** {act} **{user_display_name}** {emoji3}'
        ]

        return description_vars

    @commands.command(name='hug', aliases=('обнять',))
    async def hug(self, ctx: commands.Context, user: str):
        user = await self.user_check_and_return(ctx, user)
        if not user:
            return

        if user.id == self.bot.user.id:
            hug_gif_url = random.choice(hemu_hugs_gifs)
        else:
            hug_gif_url = random.choice(self.hug_gifs)

        description = self.choose_description(ctx.author, user, 'обнимает')
        await self.send_gif_message(ctx.channel, description, hug_gif_url)

    @commands.command(name='kiss', aliases=('поцеловать',))
    async def kiss(self, ctx: commands.Context, user: str):
        user = await self.user_check_and_return(ctx, user)
        if not user:
            return

        kiss_gif_url = random.choice(self.kiss_gifs)

        description = self.choose_description(ctx.author, user, 'целует')
        await self.send_gif_message(ctx.channel, description, kiss_gif_url)

    @commands.command(name='slap', aliases=('ударить',))
    async def slap(self, ctx: commands.Context, user: str):
        user = await self.user_check_and_return(ctx, user)
        if not user:
            return

        kiss_gif_url = random.choice(self.slap_gifs)

        description = self.choose_description(ctx.author, user, 'бьет')
        await self.send_gif_message(ctx.channel, description, kiss_gif_url)

    @staticmethod
    async def send_gif_message(channel: discord.TextChannel, description: str, gif_url: str):
        emb = discord.Embed(description=description, colour=discord.Colour.dark_purple())
        emb.set_image(url=gif_url)
        emb.set_footer(text='tenor.com', icon_url=tenor.TENOR_ICON)

        await channel.send(embed=emb)

    @commands.command(name='kyuubey', aliases=('кубей',))
    async def kubey(self, ctx: commands.Context):
        kubey_emb = discord.Embed(title=f'Уйди!', colour=discord.Color.dark_purple())
        kubey_emb.set_image(url=config.img_urls['kubey'])

        await ctx.send(embed=kubey_emb)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

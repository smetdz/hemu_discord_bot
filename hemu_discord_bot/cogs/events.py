import discord
from discord.ext import commands
from discord.utils import get

from bot import HemuBot
import config
from mongo_documents import Remind, AutoRole, Tag


class Events(commands.Cog):
    def __init__(self, bot: HemuBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        print(f'Member {member.name} left the server')

        chanel = get(member.guild.text_channels, id=config.channels['admin_ch'])

        if not chanel:
            chanel = list(member.guild.text_channels)[0]

        await chanel.send(f'Пользователь {member.name} покинул сервер.')
        self.bot.loop.create_task(self.remove_user_data_from_bd(member.id, member.guild.id))

    @staticmethod
    async def remove_user_data_from_bd(user_id: int, guild_id: int):
        docs = [Tag, Remind]
        for d in docs:
            files_ = d.find({'user_id': user_id, 'guild': guild_id})
            count = await d.count_documents({'user_id': user_id, 'guild': guild_id})
            files = await files_.to_list(count)

            for file in files:
                await file.remove()

        roles_ = AutoRole.find({'guild': guild_id})
        count = await AutoRole.count_documents({'guild': guild_id})
        roles = await roles_.to_list(count)

        for role in roles:
            user_r = list(filter(lambda r: r['user_id'] == user_id, role.active_auto_role))[0]
            role.active_auto_role.remove(user_r)
            await role.commit()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        print(f'Author: {message.author}   Content: {message.content}')
        if message.author == self.bot.user:
            return

        if self.bot.guilds_reactions_status[message.guild.id]:
            await self.reactions_on_message(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == config.HEMU_ID:
            return

        if self.bot.polls:
            try:
                await self.bot.polls[payload.message_id].update_poll(self.bot.get_user(payload.user_id), payload.emoji)
            except KeyError:
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == config.HEMU_ID:
            return

        if self.bot.polls:
            try:
                await self.bot.polls[payload.message_id].update_poll(self.bot.get_user(payload.user_id),
                                                                     payload.emoji, False)
            except KeyError:
                pass

    async def reactions_on_message(self, message: discord.Message):
        for string, reaction in self.bot.guilds_reactions[message.guild.name].items():
            if string.lower() in message.content.lower():
                if reaction.is_emb:
                    emb = discord.Embed(title='', colour=discord.Colour.dark_purple())
                    emb.set_image(url=reaction.rct)
                    await message.channel.send(embed=emb)
                    return
                await message.channel.send(reaction.rct)
                return


def setup(bot: HemuBot):
    bot.add_cog(Events(bot))

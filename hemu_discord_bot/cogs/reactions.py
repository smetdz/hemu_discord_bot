import discord
from discord.ext import commands

from umongo import fields

from bot import HemuBot
from config import hemu_emoji
from mongo_documents import Guild, Reaction


class ReactionCog(commands.Cog):
    def __init__(self, bot: HemuBot):
        self.bot = bot

    @commands.group(name='reaction', invoke_without_command=True)
    async def reaction(self, ctx: commands.Context):
        pass

    @reaction.command(name='add')
    @commands.has_permissions(administrator=True)
    async def add_reaction(self, ctx: commands.Context, string: str, reaction: str, is_emb: str = None):
        is_emb = True if is_emb in ['-e', '-emb'] else False

        if is_emb:
            try:
                emb = discord.Embed(title='', colour=discord.Colour.dark_purple())
                emb.set_image(url=reaction)
                await ctx.send(embed=emb)
            except discord.errors.HTTPException:
                await ctx.send('При использовании эмбеда реакция должна быть ссылкой на изображение/гифку.')
                return
        else:
            try:
                await ctx.send(reaction)
            except discord.errors.HTTPException:
                await ctx.send('Неверные данные.')
                return

        try:
            reaction_g = Reaction(
                string=string.lower(),
                reaction=reaction,
                is_emb=is_emb,
                guild=fields.Reference(Guild, ctx.guild.id)
            )
            await reaction_g.commit()
            self.bot.add_reaction(ctx.guild.name, string.lower(), reaction, is_emb)
            await ctx.send('Реакция была успешно создана.')
        except Exception as e:
            await ctx.send(f'При создании реакции произошла ошибка, попробуйте еще раз.{hemu_emoji["sad_hemu"]}')
            print(e)

    @reaction.command(name='remove', aliases=['del', 'delete'])
    @commands.has_permissions(administrator=True)
    async def remove_reaction(self, ctx: commands.Context, string: str):
        reaction = await Reaction.find_one({'string': string.lower()})

        if reaction:
            await reaction.remove()
            await ctx.send(f'Реакция "{reaction.string} : {reaction.reaction}" была удалена.')
            self.bot.remove_reaction(ctx.guild.name, string.lower())
            return

        await ctx.send(f'Нету реакции на "{string}".')

    @reaction.command(name='list', aliases=['lst', 'show'])
    async def reaction_list(self, ctx: commands.Context):
        reactions_ = Reaction.find({'guild': ctx.guild.id})
        count = await Reaction.count_documents({'guild': ctx.guild.id})
        reactions = await reactions_.to_list(count)
        print(reactions)

        if reactions:
            reactions_dsr = '\n'.join([f'{reaction.string} : {reaction.reaction}' for reaction in reactions])
            emb = discord.Embed(title=f'Реакции на сервере {ctx.guild.name}', colour=discord.Colour.dark_purple(),
                                description=reactions_dsr)
            emb.set_author(icon_url=self.bot.user.avatar_url, name='Hemu')
            emb.set_footer(text=f'Запрошено {ctx.author.name}')

            await ctx.send(embed=emb)
            return

        await ctx.send('На сервере отсутствуют реакции.')

    @reaction.command(name='switch', aliases=['swh'])
    @commands.has_permissions(administrator=True)
    async def switch_guild_reactions_status(self, ctx: commands.Context):
        guild = await Guild.find_one({'_id': ctx.guild.id})

        prev_status = guild.reactions_status

        guild.reactions_status = not prev_status
        self.bot.guilds_reactions_status[ctx.guild.id] = not prev_status

        await guild.commit()

        if prev_status:
            message = f'Реакции выключены.{hemu_emoji["sad_hemu"]}'
        else:
            message = f'Реакции включены.{hemu_emoji["hemu_fun"]}'

        await ctx.send(message)


def setup(bot: HemuBot):
    bot.add_cog(ReactionCog(bot))

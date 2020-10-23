import discord
from discord.ext import commands


class ListView:
    emojis = ['⬅', '➡', '❌']

    def __init__(self, title: str, count_on_page: int, page: int, count: int, search_d: dict, doc,
                 author: discord.Member = None, bot: commands.Bot = None):
        self.title = title
        self.per_page = count_on_page
        self.count = count
        self.pages_count = self.count // self.per_page + 1
        self.search_d = search_d
        self.doc = doc
        self.current_page = page if page <= self.pages_count else 1
        self.author = author
        self.bot = bot

        self.message = None

    async def show(self, channel: discord.TextChannel):
        cursor = self.doc.find(self.search_d, limit=self.per_page, skip=(self.current_page - 1) * self.per_page)
        elements = await cursor.to_list(self.per_page)

        embed = self.create_view_embed(elements)

        self.message = await channel.send(embed=embed)

        if self.pages_count > 1:
            for emoji in self.emojis:
                await self.message.add_reaction(emoji)
        else:
            await self.message.add_reaction(self.emojis[2])

        return self.message.id

    async def update(self, emoji: discord.Emoji):
        if emoji.name == self.emojis[0]:
            if self.current_page == 1:
                self.current_page = self.pages_count
            else:
                self.current_page -= 1
        elif emoji.name == self.emojis[1]:
            if self.current_page == self.pages_count:
                self.current_page = 1
            else:
                self.current_page += 1
        elif emoji.name == self.emojis[2]:
            await self.message.delete()
            return
        else:
            return

        cursor = self.doc.find(self.search_d, limit=self.per_page, skip=(self.current_page - 1) * self.per_page)
        elements = await cursor.to_list(self.per_page)

        embed = self.create_view_embed(elements)
        await self.message.edit(embed=embed)

    def calc_elem_pos(self, ind: int) -> int:
        return ind + (self.current_page - 1) * self.per_page

    def create_view_embed(self, c_lst: list) -> discord.Embed:
        pass


class TagsListView(ListView):
    def create_view_embed(self, tags: list) -> discord.Embed:
        tags_emb = discord.Embed(title=self.title, colour=discord.Colour.dark_purple(),
                                 description='\n'.join([f'**{self.calc_elem_pos(i + 1)}.** '
                                                        f'{tag.name}' for i, tag in enumerate(tags)]))
        tags_emb.set_footer(text=f'Страница {self.current_page}/{self.pages_count}')
        return tags_emb


class ReactionsListView(ListView):
    def create_view_embed(self, reactions: list) -> discord.Embed:
        reactions_dsr = '\n'.join([f'**{self.calc_elem_pos(i + 1)}.** {reaction.string} : {reaction.reaction}'
                                   for i, reaction in enumerate(reactions)])
        emb = discord.Embed(title=f'Реакции на сервере {self.title}', colour=discord.Colour.dark_purple(),
                            description=reactions_dsr)
        emb.set_author(icon_url=self.bot.user.avatar_url, name='Hemu')
        emb.set_footer(text=f'Страница {self.current_page}/{self.pages_count} | Запрошено {self.author.name}')

        return emb

import datetime
import asyncio

import discord

from config import poll_emoji, HEMU_ID
from cogs.utils.errors import InvalidPoll


class Option:
    def __init__(self, count: int, description: str):
        self.count = count
        self.description = description


class Poll:
    def __init__(self, poll_title: str, option_for_votes: tuple, creator: discord.Member,
                 mention_role: str, message: discord.Message = None):
        self.poll_title = poll_title
        self.options_for_voting = self.create_options_dict(option_for_votes)
        self.creator = creator
        self.mention_role = mention_role
        self.who_voted = []
        self.number_of_voters = 0
        self.message = message
        self.timestamp = None
        self.removed_reactions = []
        self.async_lock = asyncio.Lock()

    @staticmethod
    def create_options_dict(option_for_votes: tuple) -> dict:
        return {item[0]: Option(0, item[1]) for item in option_for_votes}

    async def create_poll(self, channel: discord.TextChannel):
        self.timestamp = datetime.datetime.utcnow()
        poll_embed = self.create_poll_emb()

        self.message = await channel.send(self.mention_role, embed=poll_embed)

        for emoji in self.options_for_voting.keys():
            try:
                await self.message.add_reaction(emoji)
            except Exception as e:
                print(e)
                await self.message.delete()
                raise InvalidPoll

        return self.message.id

    async def resume_poll(self):
        for reaction in self.message.reactions:
            async for user in reaction.users():
                if user.id not in self.who_voted and user.id != HEMU_ID:
                    self.who_voted.append(user.id)
                    self.options_for_voting[str(reaction.emoji)].count += 1
                    self.number_of_voters += 1
                elif user.id == HEMU_ID:
                    continue
                else:
                    await reaction.remove(user)

        self.timestamp = self.message.created_at
        poll_emb = self.create_poll_emb()
        await self.message.edit(embed=poll_emb)

        return self.message.id

    async def update_poll(self, user: discord.User, emoji: discord.Emoji, on_add: bool = True):
        async with self.async_lock:
            if not on_add:
                if (user, emoji) in self.removed_reactions:
                    self.removed_reactions.remove((user, emoji))
                    return

            if on_add and user.id in self.who_voted or str(emoji) not in self.options_for_voting.keys():
                await self.message.remove_reaction(emoji, user)
                self.removed_reactions.append((user, emoji))
                return

            if on_add:
                self.options_for_voting[str(emoji)].count += 1
                self.number_of_voters += 1
                self.who_voted.append(user.id)
            else:
                self.options_for_voting[str(emoji)].count -= 1
                self.number_of_voters -= 1
                self.who_voted.remove(user.id)

            poll_emb = self.create_poll_emb()
            await self.message.edit(embed=poll_emb)

    async def close_poll(self):
        emb_poll = self.create_poll_emb()
        await self.message.edit(content='', embed=emb_poll)

        max_vote_count = max(list(self.options_for_voting.values()), key=lambda opt: opt.count).count
        print(max_vote_count)
        winners = list(filter(lambda opt: opt.count == max_vote_count, list(self.options_for_voting.values())))

        if len(winners) == 1:
            await self.message.channel.send(f'Голосование "**{self.poll_title}**" завершено,'
                                            f' вариант набравший наибольшее кол-во голосов:'
                                            f'\n- {winners[0].description}')
        else:
            print(winners)
            opts = '\n'.join([f'- {win.description}' for win in winners])
            await self.message.channel.send(f'Голосование "**{self.poll_title}**" завершено,'
                                            f' варианты набравшие наибольшее кол-во голосов: \n{opts}')

    def create_poll_emb(self) -> discord.Embed:
        poll_embed = discord.Embed(title=self.poll_title, colour=discord.Colour.dark_purple())

        for emoji, option in self.options_for_voting.items():
            percent = option.count / self.number_of_voters * 100 if self.number_of_voters else 0
            progress = int(percent // 5)

            field_name = f'{emoji} - {option.description}'
            field_value = f'{poll_emoji["white"] * progress}{poll_emoji["black"] * (20 - progress)}  {int(percent)}%'
            poll_embed.add_field(name=field_name, value=field_value, inline=False)

        poll_embed.set_footer(icon_url=self.creator.avatar_url, text=f'Создано {self.creator.display_name}')
        poll_embed.timestamp = self.timestamp

        return poll_embed

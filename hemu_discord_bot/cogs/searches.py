from discord.ext import commands

from cogs.services.openweather import OpenWeatherRef
from cogs.utils import embeds


class Searches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='погода', aliases=('w', 'weather'))
    async def weather(self, ctx: commands.Context, *, city: str):
        weather = await OpenWeatherRef().get_weather(city)
        if weather:
            print(f'weather: {weather}')
            weather_emb = embeds.create_weather_emb(city, weather)

            await ctx.send(embed=weather_emb)
            return

        await ctx.send(f'Не знаю такого города как "**{city}**", попробуй еще раз.')


def setup(bot: commands.Bot):
    bot.add_cog(Searches(bot))
import os
import aiohttp
import datetime

import discord
from discord.ext import commands


class WeatherCog(commands.Cog):
    BASE_URL = 'http://openweathermap.org/'
    API_URL = 'http://api.openweathermap.org/data/2.5/'

    def __init__(self, bot):
        self.bot = bot
        self.icons_url = self.BASE_URL + 'img/wn/{}@4x.png'
        self.logo_url = self.BASE_URL + 'themes/openweathermap/assets/vendor/owm/img/icons/logo_60x60.png'

    @commands.command(name='погода')
    async def weather(self, ctx: commands.Context, *, city: str):
        data = await self.get_weather_data(city)
        if data:
            weather_data = data['weather'][0]
            weather_data.update(data['main'])
            print(f'Weather data: {weather_data}')

            weather_emb = self.create_weather_emb(city, weather_data)

            await ctx.send(embed=weather_emb)
            return

        await ctx.send(f'Не знаю такого города как "**{city}**", попробуй еще раз.')

    async def get_weather_data(self, city: str):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url=f'{self.API_URL}weather?'
                                             f'q={city}&'
                                             f'appid={os.environ["OPEN_WEATHER_KEY"]}&'
                                             f'lang=ru&'
                                             f'units=metric')

            if response.status == 404:
                return

            data = await response.json()
            return data

    def create_weather_emb(self, city: str, weather_data: dict):
        weather_emb = discord.Embed(title=f'**{weather_data["description"].title()}**',
                                    colour=discord.Color.dark_purple())

        weather_emb.set_author(name=f'{city}'.title())

        weather_emb.set_thumbnail(url=self.icons_url.format(weather_data['icon']))

        weather_emb.add_field(name='Температура', value=f'{weather_data["temp"]} °C')
        weather_emb.add_field(name='Макс. температура', value=f'{weather_data["temp_max"]} °C')
        weather_emb.add_field(name='Давление', value=f'{weather_data["pressure"]}  мбар')
        weather_emb.add_field(name='Ощущается как', value=f'{weather_data["feels_like"]} °C')
        weather_emb.add_field(name='Мин. температура', value=f'{weather_data["temp_min"]} °C')
        weather_emb.add_field(name='Влажность', value=f'{weather_data["humidity"]}%')

        weather_emb.set_footer(text='OpenWeather', icon_url=self.logo_url)

        weather_emb.timestamp = datetime.datetime.utcnow()

        return weather_emb


def setup(bot: commands.Bot):
    bot.add_cog(WeatherCog(bot))
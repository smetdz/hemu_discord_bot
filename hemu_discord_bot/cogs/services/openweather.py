import os

import aiohttp


class Weather:
    def __init__(self,  **kwargs):
        self.logo = kwargs['logo']
        self.city = kwargs['city']
        self.description = kwargs['description']
        self.weather_icon = kwargs['icon']
        self.temp = kwargs['temp']
        self.temp_max = kwargs['temp_max']
        self.temp_min = kwargs['temp_min']
        self.feels_like = kwargs['feels_like']
        self.pressure = kwargs['pressure']
        self.humidity = kwargs['humidity']

    def __str__(self):
        return '\n'.join([f'{key}: {value}' for key, value in self.__dict__.items()])


class OpenWeatherRef:
    BASE_URL = 'http://openweathermap.org/'
    API_URL = 'http://api.openweathermap.org/data/2.5/'
    logo_url = BASE_URL + 'themes/openweathermap/assets/vendor/owm/img/icons/logo_60x60.png'

    async def get_weather(self, city: str) -> Weather or None:
        weather_data_ = await self._get_weather_data(city)
        if weather_data_:
            weather_data = weather_data_['weather'][0]
            weather_data.update(weather_data_['main'])
            weather_data['icon'] = self.BASE_URL + f'img/wn/{weather_data["icon"]}@4x.png'

            return Weather(logo=self.logo_url, city=city, **weather_data)

        return None

    async def _get_weather_data(self, city: str) -> dict or None:
        url = f'{self.API_URL}weather?'\
              f'q={city}&'\
              f'appid={os.environ["OPEN_WEATHER_KEY"]}&'\
              f'lang=ru&'\
              f'units=metric'

        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                if response.status == 404:
                    return

                return await response.json()


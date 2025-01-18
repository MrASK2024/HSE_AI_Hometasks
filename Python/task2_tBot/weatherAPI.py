import requests
from config import API_KEY

class WeatherAPI:
    @staticmethod
    async def get_weather(city):
        temperature = await WeatherAPI.get_temperature(city)
        return temperature

    @staticmethod
    async def create_weather_api_url(lat, lon):
        api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        return api_url

    @staticmethod
    async def create_location_name_api_url(city):
        api_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={1}&appid={API_KEY}"
        return api_url

    @staticmethod
    async def fetch_data(url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Обработка ошибок HTTP статус-кодов
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при запросе API: {str(e)}")
            return None  # Возврат None в случае ошибки

    @classmethod
    async def get_lat_lon_city(cls, city):
        url_location_name = await cls.create_location_name_api_url(city)
        location_name_response = await cls.fetch_data(url_location_name)

        if location_name_response and len(location_name_response) > 0:
            lat = location_name_response[0]['lat']
            lon = location_name_response[0]['lon']
            return lat, lon
        else:
            return None, None

    @classmethod
    async def get_temperature(cls, city):
        lat, lon = await cls.get_lat_lon_city(city)

        if lat is None or lon is None:
            print(f"Не удалось получить координаты для города: {city}")
            return None

        url_weather = await cls.create_weather_api_url(lat, lon)
        weather_response = await cls.fetch_data(url_weather)

        if weather_response is not None and 'main' in weather_response:
            current_temp = weather_response['main']['temp']
            print(f'Текущая температура в {city}: {current_temp}')
            return current_temp
        else:
            print("Ошибка получения данных о погоде.")
            return None




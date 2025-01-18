import requests
from config import API_KEY

class WeatherAPI:
    def get_weather(self, city):
        return {'temperature': self.get_temperature(city)
            }

    async def create_weather_api_url(self, lat, lon):
        api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        return api_url


    async def cteate_location_name_api_url(self, city):
        api_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={1}&appid={API_KEY}"
        return api_url


    async def fetch_data(self, url):
        try:
            response = requests.get(url)
            return response.json()
        except Exception as e:
            # st.error(f"Ошибка при запросе API: {response.status_code}")
            return ["error 401"]


    async def get_lat_lon_city(self, city):
        url_location_name = await self.cteate_location_name_api_url(city)
        location_name_response = await self.fetch_data(url_location_name)
        name_city = location_name_response[0]['name']
        lat = location_name_response[0]['lat']
        lon = location_name_response[0]['lon']
        return lat, lon, name_city


    async def get_temperature(self, city):
        lat, lon, name_city = await self.get_lat_lon_city(city)
        print(f'name_city = {name_city}')
        print(f'lat: {lat}, lon: {lon}')

        url_weather = await self.create_weather_api_url(lat, lon)
        weather_response = await self.fetch_data(url_weather)
        current_temp = weather_response['main']['temp']
        print(f'current_temp = {current_temp}')
        return current_temp


        # для теста введите свой API ключ в поле API_KEY
        # start_time = time.time()
        # for city in names_city:
        #     await get_temperature(city)
        # end_time = time.time() - start_time
        # print(f'время получения текущей температуры c синхронным подходом: {end_time}')




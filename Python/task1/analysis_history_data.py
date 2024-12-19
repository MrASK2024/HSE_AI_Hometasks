import pandas as pd
import asyncio
import time
import requests
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from concurrent.futures import ThreadPoolExecutor

API_KEY = None


def get_moving_average_temp(data_city: pd.DataFrame):
    data_city['moving_average_mean'] = data_city['temperature'].transform(lambda x: x.rolling(window=30).mean())
    data_city['moving_average_std'] = data_city['temperature'].transform(lambda x: x.rolling(window=30).std())
    
    data_city['anomalies_temp'] = data_city['anomalies_temp'] = (
    (np.round(data_city['temperature'], 2) < np.round(data_city['moving_average_mean'] - 2 * data_city['moving_average_std'], 2)) |
    (np.round(data_city['temperature'], 2) > np.round(data_city['moving_average_mean'] + 2 * data_city['moving_average_std'], 2)))
    
    return data_city[['timestamp', 'temperature', 'moving_average_mean', 'moving_average_std', 'anomalies_temp']]

def get_mean_std(data_city: pd.DataFrame):
    data_profile_season = data_city.groupby(['season']).agg(
        {
        'temperature': ('mean', 'std')
        }
    ).reset_index()
    return data_profile_season

def get_trand(data_city: pd.DataFrame):
    data_city['timestamp'] = pd.to_datetime(data_city['timestamp'])
    
    X = data_city.drop(columns=['temperature', 'city', 'season'])
    y = data_city['temperature']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    coefficients = pd.DataFrame(model.coef_, X.columns, columns=['Коэффициенты'])
    return coefficients > 0

def get_mean_min_max_temp(data_city: pd.DataFrame):
    mean = data_city['temperature'].mean()
    min = data_city['temperature'].min()
    max = data_city['temperature'].max()
    return mean, min, max

def get_data(name_city: str):
    data = pd.read_csv('temperature_data.csv')
    data_city = data[data['city'] == name_city]
    data_average = get_moving_average_temp(data_city.copy())
    data_profile_season = get_mean_std(data_city)
    trand = get_trand(data_city.copy())
    mean_temp, min_temp, max_temp = get_mean_min_max_temp(data_city)
    
    return {'name_city':name_city,
            'data_average': data_average,
            'mean_temp': mean_temp,
            'min_temp':min_temp,
            'max_temp':max_temp,
            'data_profile_season':data_profile_season,
            'trand': trand
            }

async def create_weather_api_url(lat, lon):
    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    return api_url

async def cteate_location_name_api_url(city_name):
    api_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={1}&appid={API_KEY}"
    return api_url
    

async def fetch_data(url):
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        # st.error(f"Ошибка при запросе API: {response.status_code}")
        return ["error 401"]

async def get_lat_lon_city(name_city):
    url_location_name = await cteate_location_name_api_url(name_city)
    location_name_response = await fetch_data(url_location_name)
    name_city = location_name_response[0]['name']
    lat = location_name_response[0]['lat']
    lon = location_name_response[0]['lon']
    return lat, lon, name_city

async def get_temperature(name_city):
    lat, lon, name_city = await get_lat_lon_city(name_city)
    print(f'name_city = {name_city}')
    print(f'lat: {lat}, lon: {lon}')

    url_weather = await create_weather_api_url(lat, lon)
    weather_response = await fetch_data(url_weather)
    current_temp = weather_response['main']['temp']
    print(f'current_temp = {current_temp}')
    return current_temp

async def get_temp(names_city):
    tasks = [get_temperature(city) for city in names_city]
    start_time = time.time()
    current_temp = await asyncio.gather(*tasks)
    end_time = time.time() - start_time
    print(f'время получения текущей температуры с асинхронным подходом: {end_time}')
    return current_temp
        
    
    # для теста введите свой API ключ в поле API_KEY
    # start_time = time.time()
    # for city in names_city:
    #     await get_temperature(city)
    # end_time = time.time() - start_time
    # print(f'время получения текущей температуры c синхронным подходом: {end_time}')
    
def get_data_parallel_apply(names_city):
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(get_data, names_city))
    return results 

def check_anomaly(current_temp, data_profile_season, current_season = 'winter'):
    mean = data_profile_season[data_profile_season['season'] == current_season ]['temperature']['mean']
    std = data_profile_season[data_profile_season['season'] == current_season ]['temperature']['std']
    
    lower_threshold = (mean - 2 * std).values[0]
    upper_threshold = (mean + 2 * std).values[0]
    
    if round(current_temp,2) > round(upper_threshold,2) or round(current_temp,2) < round(lower_threshold,2):
        return True
    else:
        return False

# names_city = ['New York', 'Moscow', 'London']
# start_time = time.time()
# result = get_data_parallel_apply(names_city)
# end_time = time.time() - start_time   
# print(f'время выполнения с распаралеливанием задач: {end_time}')

# start_time = time.time()
# for city in names_city:
#     get_data(city)
# end_time = time.time() - start_time   
# print(f'время выполнения без распаралеливанием задач: {end_time}')
  
  
# asyncio.run(get_temp(names_city))


    
import streamlit as st
import pandas as pd
import analysis_history_data as ahd
import asyncio
import matplotlib.pyplot as plt

DATA = None
API_KEY = None

st.title("Сервис для получения статистических данных о температуре в городе")
st.header("Шаг 1: Загрузка данных")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

if uploaded_file is not None:
    with open('temperature_data.csv', 'wb') as csvFile:
        csvFile.write(uploaded_file.getbuffer())
    
    DATA = pd.read_csv(uploaded_file)
    DATA['timestamp'] = pd.to_datetime(DATA['timestamp'])
    st.write("Превью данных:")
    st.dataframe(DATA)
else:
    st.write("Пожалуйста, загрузите CSV-файл.")
    
if DATA is not None:
    st.header("Шаг 2: Выбор города")
    city = st.selectbox("Выберите город для мониторинга текущей температуры", DATA['city'].unique())
   
    st.header("Шаг 3: Введите API-ключ OpenWeatherMap")
    
    try:
        ahd.API_KEY = st.text_input("Введите API-ключ")
        if not ahd.API_KEY:
            st.warning("Пожалуйста, введите ваш API-ключ.")
        else:
            current_temp = asyncio.run(ahd.get_temp([city]))
            if ahd.API_KEY:
                st.success("API-ключ успешно получен!")
                
    except Exception:
        st.write('{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}')

    st.header("Шаг 4: Основные статистики")
    if st.checkbox("Показать описательную статистику по историческим данным для города"):
        st.write(DATA[DATA["city"] == city].describe())
            
    st.header("Шаг 5: Визуализация данных")
    st.subheader("Временной ряд температур с выделением аномалий ")
    data_satatistic =ahd.get_data_parallel_apply([city])
    
    data_average = data_satatistic[0]['data_average']
    anomalies_temp = data_average[data_average['anomalies_temp'] == True]
    
    data_city = DATA[DATA["city"] == city]
    data_city.set_index('timestamp', inplace=True)
    anomalies_temp.set_index('timestamp', inplace=True)
    
    plt.figure(figsize=(14, 7))
    plt.plot(data_city.index, data_city['temperature'], label='Температура', color='lightblue')
    plt.scatter(anomalies_temp.index, anomalies_temp['temperature'], color='lightcoral', label='Аномалии', zorder=5)
    
    plt.xlabel('Дата')
    plt.ylabel('Температура (°C)')
    st.pyplot(plt)
    
    st.subheader("Сезонные профили с указанием среднего и стандартного отклонения")
    fig, ax = plt.subplots()
    mean_temp = data_satatistic[0]['mean_temp']
    min_temp = data_satatistic[0]['min_temp']
    max_temp = data_satatistic[0]['max_temp']
    data_profile_season = data_satatistic[0]['data_profile_season']
    
    plt.bar(DATA['season'].unique(), data_profile_season['temperature']['mean'], yerr=data_profile_season['temperature']['std'], 
            capsize=5, color='lightblue')
    
    plt.xlabel('Сезон')
    plt.ylabel('Средняя температура (°C)')
    st.pyplot(fig)
    
    st.subheader(f'Для {city} зафиксированы:')
    st.subheader(f'минимальная температура {int(min_temp)}°C')
    st.subheader(f'максимальная температура {int(max_temp)}°C')
    st.subheader(f' средняя температура {int(mean_temp)}°C')

    st.header("Шаг 6: Отображение текущей температуры и проверка ее на аномальность для текущего сезона")
    season = st.selectbox("Выберите текущий сезон", DATA['season'].unique())
    if season in DATA['season'].unique():
        if ahd.check_anomaly(current_temp[0], data_profile_season, current_season = season):
            st.warning(f"Текущая температура {current_temp[0]} является аномальной")
        else:
            st.success(f"Текущая температура {current_temp[0]} является нормальной")

        
    
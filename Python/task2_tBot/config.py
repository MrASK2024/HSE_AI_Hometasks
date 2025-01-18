import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена")

API_KEY = os.getenv("WEATHER_API_KEY")

if not API_KEY:
    raise ValueError("Переменная окружения WEATHER_API_KEY не установлена")
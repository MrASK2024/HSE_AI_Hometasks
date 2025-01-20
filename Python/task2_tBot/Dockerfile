FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Установите переменную окружения для порта
ENV PORT=8080

# Команда запуска
CMD ["python", "bot.py"]

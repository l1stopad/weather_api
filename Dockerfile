# Базовий образ для Python
FROM python:3.11-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо залежності
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код додатка в контейнер
COPY . /app/

# Відкриваємо порт для FastAPI
EXPOSE 8000

# Команда для запуску сервера FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

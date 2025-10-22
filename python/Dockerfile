FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

ENV PYTHONUNBUFFERED=1

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 bot && chown -R bot:bot /app
USER bot

# Запускаем бота
CMD ["python", "main.py"]

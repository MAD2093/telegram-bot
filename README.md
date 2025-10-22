# Telegram Bot для мониторинга арбитражных возможностей

(AI generated)

Система из двух ботов для Telegram:
1. **Go бот** - получает данные из Redis и отправляет арбитражные пары пользователям по их фильтрам
2. **Python бот** - управляет настройками фильтров пользователей

## Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis         │    │   PostgreSQL    │    │   Telegram      │
│   (арбитражные  │    │   (пользователи │    │   (пользователи)│
│    пары)        │    │    и фильтры)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Go Bot        │    │   Python Bot    │    │   Пользователи  │
│   (отправка     │    │   (настройка    │    │   (получают     │
│    пар)         │    │    фильтров)    │    │    уведомления) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Компоненты

### Go Bot (`src/`)
- Подписывается на Redis канал `arbitrage:spot:update`
- Загружает пользователей и фильтры из PostgreSQL
- Фильтрует пары по настройкам каждого пользователя
- Отправляет подходящие пары в Telegram

### Python Bot (`filter_bot/`)
- Управляет настройками фильтров пользователей
- Команды для изменения спреда, объема, комиссии
- Управление черными списками бирж, монет, сетей
- Интерактивные inline-кнопки

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository>
cd tg_bot
```

### 2. Настройка переменных окружения
```bash
cp env.example .env
# Отредактируйте .env файл, указав ваш TELEGRAM_BOT_TOKEN
```

### 3. Запуск через Docker Compose
```bash
docker-compose up -d
```

### 4. Проверка работы
```bash
docker-compose logs -f
```

## Переменные окружения

Создайте файл `.env` на основе `env.example`:

```bash
# Telegram Bot Token (общий для обоих ботов)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# PostgreSQL настройки
DB_NAME=tg_bot
DB_USER=postgres
DB_PASSWORD=your_strong_password_here

# Redis настройки
REDIS_PASSWORD=your_redis_password_here
```

## Команды Python бота

### Основные команды
- `/start` - регистрация пользователя
- `/filters` - просмотр текущих фильтров
- `/set_spread <значение>` - установка минимального спреда
- `/set_volume <мин> <макс>` - установка диапазона объема
- `/set_fee <значение>` - установка максимальной комиссии

### Управление черными списками
- `/blacklist_exchange <add/remove> <exchange>` - биржи
- `/blacklist_coin <add/remove> <coin>` - монеты
- `/blacklist_network <add/remove> <network>` - сети

## Структура базы данных

```sql
-- Основная таблица пользователей
CREATE TABLE bot_users (
  tg_id BIGINT PRIMARY KEY,
  active BOOLEAN DEFAULT TRUE,
  spread_min DOUBLE PRECISION DEFAULT 0,
  volume_min DOUBLE PRECISION DEFAULT 0,
  volume_max DOUBLE PRECISION DEFAULT 0,
  total_fee DOUBLE PRECISION DEFAULT 0
);

-- Черный список бирж для депозита
CREATE TABLE deposit_exchanges (
  id SERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES bot_users(tg_id) ON DELETE CASCADE,
  name VARCHAR(50) NOT NULL,
  UNIQUE(user_id, name)
);

-- Черный список бирж для вывода
CREATE TABLE withdraw_exchanges (
  id SERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES bot_users(tg_id) ON DELETE CASCADE,
  name VARCHAR(50) NOT NULL,
  UNIQUE(user_id, name)
);

-- Черный список монет
CREATE TABLE blacklisted_coins (
  id SERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES bot_users(tg_id) ON DELETE CASCADE,
  name VARCHAR(20) NOT NULL,
  UNIQUE(user_id, name)
);

-- Черный список сетей
CREATE TABLE blacklisted_nets (
  id SERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES bot_users(tg_id) ON DELETE CASCADE,
  name VARCHAR(30) NOT NULL,
  UNIQUE(user_id, name)
);

-- Индексы для быстрого поиска
CREATE INDEX idx_deposit_exchanges_user_id ON deposit_exchanges(user_id);
CREATE INDEX idx_withdraw_exchanges_user_id ON withdraw_exchanges(user_id);
CREATE INDEX idx_blacklisted_coins_user_id ON blacklisted_coins(user_id);
CREATE INDEX idx_blacklisted_nets_user_id ON blacklisted_nets(user_id);
```

## Разработка

### Локальный запуск Go бота
```bash
cd src
go mod download
go run main.go
```

### Локальный запуск Python бота
```bash
cd filter_bot
pip install -r requirements.txt
python main.py
```

### Локальный запуск PostgreSQL
```bash
docker run -d --name postgres \
  -e POSTGRES_DB=tg_bot \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine
```

### Локальный запуск Redis
```bash
docker run -d --name redis \
  -e REDIS_PASSWORD=password \
  -p 6379:6379 \
  redis:7-alpine
```

## Мониторинг

- Go бот: логирует загруженных пользователей и отправленные пары
- Python бот: логирует команды пользователей и изменения в БД
- PostgreSQL: доступен на порту 5432
- Redis: доступен на порту 6379

## Требования

- Docker и Docker Compose
- Go 1.22+ (для локальной разработки)
- Python 3.11+ (для локальной разработки)
- PostgreSQL 15+
- Redis 7+
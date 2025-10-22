import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ENV
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "tg_bot")
REDIS_ADDR = os.getenv("REDIS_ADDR", "localhost:6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
GRPC_PORT = os.getenv("GRPC_PORT", "50051")
GRPC_ADDR = os.getenv("GRPC_ADDR", "localhost")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

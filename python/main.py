import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config.main import BOT_TOKEN, REDIS_ADDR, REDIS_PASSWORD
from database.main import engine
from database.models import Base
from handlers.commands import router
from handlers.callbacks import callback_router

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Bot init
    bot = Bot(token=BOT_TOKEN)
    
    # Redis setup
    host, port = REDIS_ADDR.split(":")
    redis_url = f"redis://:{REDIS_PASSWORD}@{host}:{port}" if REDIS_PASSWORD else f"redis://{host}:{port}"
    storage = RedisStorage.from_url(redis_url)
    
    # Создаем Dispatcher с storage
    dp = Dispatcher(storage=storage)
    
    # Подключаем routers
    dp.include_router(router)
    dp.include_router(callback_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot_config import TOKEN
from app.handlers import router
from utils.middlewares import DataBaseMiddleware
from utils.engine import async_session

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router)

    dp.message.outer_middleware(DataBaseMiddleware(session_pool=async_session))
    # dp.update.middleware(DataBaseMiddleware(session_pool=async_session))
    dp.callback_query.middleware(DataBaseMiddleware(session_pool=async_session))

    await dp.start_polling(bot)


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
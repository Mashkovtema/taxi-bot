import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from notify_admin import on_startup_notify
from database.models import async_main
from config_data.config_data import Config, load_config

from handlers import start_handler
from handlers import groups_handler
from handlers.admin_handlers import  drivers_handler, admins_handler, newslatter_handler
from handlers.user_handlers import on_the_line_handler, driver_lk_handler


# Инициализируем logger
logger = logging.getLogger(__name__)

# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,

        # filename="py_log.log",
        # filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    #Регистрация роутеров
    # Старт
    dp.include_router(start_handler.router)

    # Админ
    dp.include_router(newslatter_handler.router)
    dp.include_router(admins_handler.router)
    dp.include_router(drivers_handler.router)

    # Водители
    dp.include_router(on_the_line_handler.router)
    dp.include_router(driver_lk_handler.router)

    # Группы
    dp.include_router(groups_handler.router)

    await on_startup_notify(bot=bot)
    await async_main()


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
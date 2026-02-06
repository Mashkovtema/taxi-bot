import time
from config_data.config_data import Config, load_config
from aiogram import Bot
import logging
# from filters.error_handling import error_handler

config: Config = load_config()


# Уведомление администраторам бота о том что Бот запущен
# @error_handler
async def on_startup_notify(bot: Bot):
    logging.info('on_startup_notify')
    date_now = time.strftime("%Y-%m-%d", time.localtime())
    time_now = time.strftime("%H:%M:%S", time.localtime())
    for admin in config.tg_bot.admin_ids.split(','):
        if admin:
            try:
                text = (f"✅Бот запущен и готов к работе!"
                        f"📅Дата: {date_now}"
                        f"⏰Время: {time_now}")
                await bot.send_message(chat_id=admin, text=text)
            except Exception as err:
                pass
                # logging.exception(err)
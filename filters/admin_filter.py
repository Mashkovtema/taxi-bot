from config_data.config_data import load_config, Config
from database.requests.user_requests import get_db_admins
from aiogram.filters import BaseFilter
from aiogram.types import Message
import logging

config: Config = load_config()


async def check_super_admin(telegram_id: int) -> bool:
    """
    Проверка на администратора
    :param telegram_id: id пользователя телеграм
    :return: true если пользователь администратор, false в противном случае
    """
    logging.info('check_manager')
    list_super_admin = config.tg_bot.admin_ids.split(',')
    list_db_admins = await get_db_admins()
    return (str(telegram_id) in list_super_admin) or (int(telegram_id) in list_db_admins)


class IsSuperAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return await check_super_admin(telegram_id=message.chat.id)
import struct

from database.models import async_session, Drivers, Admins, Applications
from sqlalchemy import select, or_, and_, delete, func, case, cast, Integer, String
import logging


async def check_driver_in_db(user_id: int) -> str:
    """Проверка наличия водителя в бд"""
    logging.info('check_driver_in_db')
    async with async_session() as session:
        driver = await session.scalar(select(Drivers).where(Drivers.user_id == user_id))
        if driver:
            if driver.is_moderation == False and driver.banned == False:
                return 'dont_moderation'
            if driver.is_moderation == True and driver.banned == True:
                return 'banned'
            if driver.is_moderation == True and driver.banned == False:
                return 'good_driver'
        else:
            return 'not_in_db'


async def get_driver_data(user_id: int) -> dict:
    """Получение данных о водителе"""
    logging.info('get_driver_data')
    async with async_session() as session:
        driver_data = await session.scalar(select(Drivers).where(Drivers.user_id == user_id))
        return driver_data.__dict__


async def insert_driver_data(data: dict) -> None:
    """Занесение данных о водителе"""
    logging.info('insert_driver_data')
    async with async_session() as session:
        new_driver = Drivers(**data)
        session.add(new_driver)
        await session.commit()


async def go_or_out_of_line(driver_user_id: int, value: bool) -> None:
    """Выход на линию или сход с линии"""
    logging.info('go_or_out_of_line')
    async with async_session() as session:
        driver = await session.scalar(select(Drivers).where(Drivers.user_id == driver_user_id))
        driver.on_the_line = value
        await session.commit()


async def update_driver_data(driver_user_id: int, type_: str, value: str, username: str) -> None:
    """Обновление данных о водителе"""
    logging.info('update_driver_data')
    async with async_session() as session:
        driver = await session.scalar(select(Drivers).where(Drivers.user_id == driver_user_id))
        if type_ == 'car':
            driver.car_description = value
        if type_ == 'name':
            driver.driver_name = value
        driver.username = username
        await session.commit()


async def add_new_admin(user_id: int, id_: int) -> bool:
    """Добавление нового администратора"""
    async with async_session() as session:
        admin = await session.scalar(select(Admins).where(Admins.id == id_))
        if admin.user_id == 0:
            admin.user_id = user_id
            await session.commit()
            return True
        else:
            return False


async def get_db_admins() -> list:
    """Получение списка админов из бд"""
    async with async_session() as session:
        admins = await session.scalars(select(Admins.user_id))
        if admins:
            return admins.all()
        else:
            return []


async def get_all_drivers_ids() -> list:
    """Получение user_id всех водителей"""
    logging.info('get_all_drivers_ids')
    async with async_session() as session:
        drivers = await session.scalars(select(Drivers.user_id).where(Drivers.on_the_line == True, Drivers.banned == False, Drivers.is_moderation == True))
        if drivers:
            return drivers.all()
        else:
            return []


async def add_new_application(group_id: int, group_name: str, address: str, client_user_id: int, client_username: str, group_username: str, message_id: int) -> int:
    """Добавление новой заявки"""
    logging.info('add_new_application')
    async with async_session() as session:
        new_application = Applications(
            group_id=group_id,
            group_name=group_name,
            address=address,
            client_user_id=client_user_id,
            client_username=client_username,
            group_username=group_username,
            message_id=message_id
        )
        session.add(new_application)
        await session.flush()
        return_id = new_application.id
        await session.commit()
        return return_id


async def get_application_by_id(id_: int):
    """Получение заявки по id"""
    logging.info('get_application_by_id')
    async with async_session() as session:
        application = await session.scalar(select(Applications).where(Applications.id == id_))
        return application.__dict__


async def confirm_driver_application(driver_user_id: int,
                                     application_id: int,
                                     driver_name: str,
                                     driver_username: str,
                                     car: str,
                                     time: str,
                                     with_passenger: bool) -> bool:
    """Обновление данные по заявке"""
    logging.info('confirm_driver_application')
    async with async_session() as session:
        application = await session.scalar(select(Applications).where(Applications.id == application_id))
        if application.status == 'new':
            application.status = 'confirmed_driver'
            application.driver_user_id = driver_user_id
            application.driver_username = driver_username
            application.driver_name = driver_name
            application.car_name = car
            application.time = time
            application.with_passenger = with_passenger
            await session.commit()
            return True
        else:
            return False



async def confirm_or_not_application_by_user(application_id: int, status: str):
    """Отмена или подтверждение заявки пользователем"""
    logging.info('confirm_or_not_application_by_user')
    async with async_session() as session:
        application = await session.scalar(select(Applications).where(Applications.id == application_id))
        application.status = status
        await session.commit()












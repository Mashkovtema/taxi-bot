from database.models import async_session, Drivers, Admins, Applications
from sqlalchemy import select, or_, and_, delete, func, case, cast, Integer, String
import logging


async def get_drivers_to_moderate():
    """Получение водителей для модерации"""
    logging.info('get_drivers_to_moderate')
    async with async_session() as session:
        drivers = await session.scalars(select(Drivers).where(Drivers.is_moderation == False))
        if drivers:
            return drivers.all()
        else:
            return None


async def get_drivers_to_ban() -> list:
    """Получение списка водителей для блокировки"""
    logging.info('get_drivers_to_ban')
    async with async_session() as session:
        drivers = await session.scalars(select(Drivers).where(Drivers.is_moderation == True, Drivers.banned == False))
        if drivers:
            return drivers.all()
        else:
            return None


async def get_driver_data_by_id(id_: int) -> dict:
    """Получения информации о водителе по id"""
    logging.info('get_driver_by_id')
    async with async_session() as session:
        driver_data = await session.scalar(select(Drivers).where(Drivers.id == id_))
        return driver_data.__dict__


async def get_driver_data_by_user_id(user_id: int) -> dict:
    """Получения информации о водителе по user_id"""
    logging.info('get_driver_by_id')
    async with async_session() as session:
        driver_data = await session.scalar(select(Drivers).where(Drivers.user_id == user_id))
        return driver_data.__dict__


async def confirm_moderation_driver(driver_user_id: int) -> None:
    """Подтвердение модерации водителя"""
    logging.info('confirm_moderation_driver')
    async with async_session() as session:
        driver = await session.scalar(select(Drivers).where(Drivers.user_id == driver_user_id))
        if driver:
            driver.is_moderation = True
            await session.commit()


async def delete_driver(user_id: int) -> None:
    """Удаление водителя"""
    logging.info('delete_driver')
    async with async_session() as session:
        driver = await session.scalar(select(Drivers).where(Drivers.user_id == user_id))
        await session.delete(driver)
        await session.commit()


async def ban_driver(driver_user_id: int) -> None:
    """Блокировка водителя"""
    logging.info('ban_driver')
    async with async_session() as session:
        driver = await session.scalar(select(Drivers).where(Drivers.user_id == driver_user_id))
        if driver:
            driver.banned = True
            await session.commit()


async def get_drivers_to_unban():
    """Получение списка водителей для разблокировки"""
    logging.info('get_drivers_to_unban')
    async with async_session() as session:
        drivers = await session.scalars(select(Drivers).where(Drivers.is_moderation == True, Drivers.banned == True))
        if drivers:
            return drivers.all()
        else:
            return None


async def unban_driver(driver_id: int) -> None:
    """Разблокировка водителей"""
    logging.info('unban_driver')
    async with async_session() as session:
        driver = await session.scalar(select(Drivers).where(Drivers.id == driver_id))
        driver.banned = False
        await session.commit()


async def add_new_admin(admin_name: str) -> int:
    """Добавление нового администратора"""
    logging.info('add_new_admin')
    async with async_session() as session:
        new_admin = Admins(admin_name=admin_name)
        session.add(new_admin)
        await session.flush()
        admin_id = new_admin.id
        await session.commit()
        return admin_id


async def get_all_admins():
    """Получение всех админов"""
    logging.info('get_all_admins')
    async with async_session() as session:
        admin = await session.scalars(select(Admins))
        if admin:
            return admin.all()
        else:
            return None


async def get_admin_data_by_id(admin_id: str) -> dict:
    """Получение информации о админе"""
    logging.info('get_admin_data_by_id')
    async with async_session() as session:
        admin_data = await session.scalar(select(Admins).where(Admins.id == admin_id))
        return admin_data.__dict__


async def delete_admin(admin_id: int) -> None:
    """Удаление админа"""
    logging.info('delete-admin')
    async with async_session() as session:
        admin = await session.scalar(select(Admins).where(Admins.id == admin_id))
        await session.delete(admin)
        await session.commit()


async def get_drivers_ids_for_newsletter(type: str) -> list:
    """Получение id водителей для рассылки"""
    logging.info('get_drivers_ids_for_newsletter')
    async with async_session() as session:
        if type == 'on-line':
            drivers_ids = await session.scalars(select(Drivers.user_id).where(Drivers.on_the_line == True, Drivers.banned == False, Drivers.is_moderation == True))
        if type == 'not-on-line':
            drivers_ids = await session.scalars(select(Drivers.user_id).where(Drivers.on_the_line == False, Drivers.banned == False, Drivers.is_moderation == True))
        if type == 'all':
            drivers_ids = await session.scalars(select(Drivers.user_id))

        if drivers_ids:
            return drivers_ids.all()
        else:
            return []















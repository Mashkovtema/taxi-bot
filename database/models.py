from sqlalchemy import String, Integer, Boolean, BigInteger, MetaData, Table, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession


engine = create_async_engine("sqlite+aiosqlite:///database/database.sql")

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Drivers(Base):
    __tablename__ = 'Drivers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, default=0)
    username: Mapped[str] = mapped_column(String, default='---')
    car_description: Mapped[str] = mapped_column(String, default='---')
    driver_name: Mapped[str] = mapped_column(String, default='---')
    on_the_line: Mapped[bool] = mapped_column(Boolean, default=False)
    is_moderation: Mapped[bool] = mapped_column(Boolean, default=False)
    banned: Mapped[bool] = mapped_column(Boolean, default=False)


class Admins(Base):
    __tablename__ = 'Admins'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, default=0)
    admin_name: Mapped[str] = mapped_column(String, default='---')


class Applications(Base):
    __tablename__ = 'Applications'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String, default='new') # new, confirm_driver, confirm_user, canceled
    client_user_id: Mapped[int] = mapped_column(BigInteger, default=0)
    client_username: Mapped[str] = mapped_column(String, default='---')
    driver_user_id: Mapped[int] = mapped_column(BigInteger, default=0)
    driver_name: Mapped[str] = mapped_column(String, default='---')
    driver_username: Mapped[str] = mapped_column(String, default='---')
    group_id: Mapped[int] = mapped_column(BigInteger, default=0)
    message_id: Mapped[int] = mapped_column(BigInteger, default=0)
    group_name: Mapped[str] = mapped_column(String, default='---')
    group_username: Mapped[str] = mapped_column(String, default='---')
    address: Mapped[str] = mapped_column(String, default='---')
    car_name: Mapped[str] = mapped_column(String, default='---')
    time: Mapped[str] = mapped_column(String, default='---')
    with_passenger: Mapped[bool] = mapped_column(Boolean, default=False)



async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
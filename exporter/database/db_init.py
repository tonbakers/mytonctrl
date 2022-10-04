from exporter.database.session import async_engine
from exporter.database.base import Base
from exporter import config


async def init_database() -> None:
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

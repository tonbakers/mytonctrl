from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionClass
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm.session import sessionmaker

from exporter import config

engine = create_engine(
    config.DB_DSN,
    echo=config.DB_ECHO,
    pool_pre_ping=True,
    connect_args=dict(application_name=f'{config.APP_TITLE}_db'),
)

async_engine = create_async_engine(
    str(config.DB_DSN).replace(config.DB_DRIVER, f'{config.DB_DRIVER}+asyncpg'),
    echo=config.DB_ECHO,
    pool_pre_ping=True,
    connect_args=dict(application_name=f'{config.APP_TITLE}_async_db'),
)


AsyncSession = AsyncSessionClass(async_engine, expire_on_commit=False)
Session = sessionmaker(expire_on_commit=True, bind=engine)

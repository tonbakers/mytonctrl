from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm.session import Session

from exporter import config


engine: Engine = create_engine(
    config.DB_DSN,
    echo=config.DB_ECHO,
    pool_pre_ping=True,
    connect_args=dict(application_name=f'{config.APP_TITLE}_db'),
)

async_engine: AsyncEngine = create_async_engine(
    str(config.DB_DSN).replace(config.DB_DRIVER, f'{config.DB_DRIVER}+asyncpg'),
    echo=config.DB_ECHO,
    pool_pre_ping=True,
)

async_session = AsyncSession(
    async_engine,
    expire_on_commit=False,
    sync_session_class=Session,
)

static_session = Session(
    bind=engine,
    expire_on_commit=False,
)

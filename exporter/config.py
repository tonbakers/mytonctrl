from starlette.config import Config
from sqlalchemy.engine.url import URL, make_url

config = Config('.env')


APP_HOST = config('APP_HOST', default='127.0.0.1', cast=str)
APP_PORT = config('APP_PORT', default=5561, cast=int)
APP_TITLE = config('APP_TITLE', default='Validators monitor', cast=str)

DB_HOST = config('APP_HOST', default='127.0.0.1', cast=str)
DB_PORT = config('DB_PORT', default=5432, cast=int)
DB_DRIVER = config('DB_DRIVER', default='postgresql', cast=str)
DB_DATABASE = config('DB_DATABASE', default='validators_monitor', cast=str)
DB_USERNAME = config('DB_USERNAME', default='monitor', cast=str)
DB_PASSWORD = config('DB_PASSWORD', default='s00pa_secret', cast=str)
DB_ECHO = config('DB_ECHO', default=True, cast=bool)
DB_DSN = config(
    'DB_DSN',
    default=URL.create(
        host=DB_HOST,
        port=DB_PORT,
        drivername=DB_DRIVER,
        username=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_DATABASE,
    ),
    cast=make_url,
)

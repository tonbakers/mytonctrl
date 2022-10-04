import uvicorn

from fastapi.applications import FastAPI

from exporter import config
from exporter.api import root as root_router
from exporter.jobs.validators_job import job_get_and_store_validators_data
from exporter.database.db_init import init_database


def create_app(title: str = config.APP_TITLE) -> FastAPI:
    application = FastAPI(title=title)
    application.include_router(root_router)
    
    @application.on_event('startup')
    async def startup() -> None:
        job_get_and_store_validators_data()
    return application


if __name__ == '__main__':
    app: FastAPI = create_app()
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT)
else:
    app: FastAPI = create_app()

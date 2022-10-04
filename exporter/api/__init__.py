from fastapi.routing import APIRouter

from exporter.api.monitor.views import router as metrics_router


root = APIRouter(prefix='/api')
root.include_router(metrics_router, prefix='/metrics')

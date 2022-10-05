from fastapi.routing import APIRouter

from mytoncore import MyTonCore
from src.ton.factory import get_ton_controller

router = APIRouter()


@router.get('/')
def get_metrics():
    ton_core: MyTonCore = get_ton_controller()
    return 200

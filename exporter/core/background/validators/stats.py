import typing as t

from mytoncore import MyTonCore, local
from src.ton.factory import get_ton_controller

from .serializers import ValidatorStatistic


async def get_validators_stats() -> t.List[ValidatorStatistic]:
    # Disable "mytonctrl" logging
    local.AddLog = lambda *args: None
    ton_core: MyTonCore = get_ton_controller()
    stats = ton_core.GetValidatorsList()
    return [
        ValidatorStatistic.parse_obj(stat)
        for stat in stats
    ]

import time

from decimal import Decimal
from typing import List, Optional

from pydantic.main import BaseModel
from pydantic.fields import Field
from prometheus_client.exposition import start_http_server
from prometheus_client.metrics import Gauge

from mytoncore import MyTonCore, local
from src.ton.factory import get_ton_controller
from src.utils.click_messages import error, message, warning

validator_efficiency = Gauge(
    'validator_efficiency',
    'The gauge metric to show TON validators efficiency.',
)
ton_core: MyTonCore = get_ton_controller()


class ValidatorInfo(BaseModel):
    efficiency: Decimal
    online: bool
    pubkey: str
    adnl_address: str = Field(..., alias='adnlAddr')
    wallet_address: Optional[str] = Field(None, alias='walletAddr')


def get_metrics():
    warning('Trying to request validators information.')
    # Disable built-in logging
    local.AddLog = lambda *args: None
    ton_core.SetSettings('timeout', 300)
    data: List[ValidatorInfo] = [
        ValidatorInfo(**data)
        for data in ton_core.GetValidatorsList(False)
    ]
    message('Validators information fetched, pushing to "prometheus".')
    for validator in data:
        validator_efficiency.observe(float(validator.efficiency))


if __name__ == '__main__':
    start_http_server(5561)
    while True:
        try:
            get_metrics()
            time.sleep(60)
            message(f'Waiting for "{60}" seconds')
        except KeyboardInterrupt:
            raise message('Stopped by user!', exit_after=True)
        except Exception as err:
            raise error(
                'Occurred unhandled exception!',
                *err.args,
            )

import time

from decimal import Decimal
from typing import Dict, List, Optional

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.error_wrappers import ValidationError
from prometheus_client.exposition import start_http_server
from prometheus_client.metrics import Histogram

from mytoncore import MyTonCore, local
from src.ton.factory import get_ton_controller
from src.ton.addr import parse_base64_address
from src.utils.click_messages import error, message, warning

ton_core: MyTonCore = get_ton_controller()

VALIDATOR_UNITS_MAP: Dict[str, Histogram] = {}


class ValidatorInfo(BaseModel):
    efficiency: Decimal = 0.0
    online: bool
    pubkey: str
    adnl_address: str = Field(..., alias='adnlAddr')
    wallet_address: Optional[str] = Field(None, alias='walletAddr')


def get_metrics():
    warning('Trying to request validators information.')
    # Disable built-in logging
    local.AddLog = lambda *args: None
    ton_core.SetSettings('timeout', 300)
    data = []
    fetching_start = time.time()
    for info in ton_core.GetValidatorsList(False):
        try:
            data.append(ValidatorInfo(**info))
        except ValidationError as validation_err:
            warning('Occurred unhandled validation error:', *validation_err.args)
            continue
    fetching_end = time.time()
    message(f'Fetched info for "{len(data)}" validators. Elapsed time: {fetching_end - fetching_start} sec')
    for validator_info in data:
        if validator_info.online is True:
            if validator_info.wallet_address in VALIDATOR_UNITS_MAP:
                continue
            if validator_info.wallet_address is not None:
                _, full_address, _, _ = parse_base64_address(validator_info.wallet_address)
                VALIDATOR_UNITS_MAP[validator_info.wallet_address]: Histogram = Histogram(
                    name='validator_efficiency',
                    documentation='The gauge metric to show TON validators efficiency.',
                    unit=full_address,
                )
                continue
            warning(
                'Failed to get wallet address '
                f'for validator with public key: "{validator_info.pubkey}"'
            )
    online_validators: List[ValidatorInfo] = [validator for validator in data if validator.online is True]
    offline_validators: List[ValidatorInfo] = [validator for validator in data if validator.online is False]
    message(
        'Validators online status:',
        f'Online: {len(online_validators)}',
        f'Offline: {len(offline_validators)}',
    )
    for validator_info in data:
        if validator_info.online is True:
            metric: Optional[Histogram] = VALIDATOR_UNITS_MAP.get(validator_info.wallet_address)
            if validator_info.wallet_address is None and metric is None:
                error(f'Metric instance not found for validator with public key: "{validator_info.adnl_address}"')
                continue
            metric.observe(float(validator_info.efficiency))
    message('Data successfully stored.')


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

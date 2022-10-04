from decimal import Decimal

from pydantic.main import BaseModel
from pydantic.fields import Field


class ValidatorStatistic(BaseModel):
    efficiency: Decimal = Decimal(0.0)
    online: bool = False
    adnl_address = Field('MISSING', alias='adnlAddr')
    wallet_address = Field('MISSING', alias='walletAddr')
    public_key: str = Field('MISSING', alias='pubkey')

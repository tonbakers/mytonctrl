import typing as t

from decimal import Decimal

from pydantic.main import BaseModel
from pydantic.fields import Field


class ValidatorStatistic(BaseModel):
    efficiency: Decimal = Decimal(0.0)
    online: bool = False
    adnl_address: t.Optional[str] = Field(None, alias='adnlAddr')
    wallet_address: t.Optional[str] = Field(None, alias='walletAddr')
    public_key: t.Optional[str] = Field(None, alias='pubkey')

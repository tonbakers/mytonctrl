import typing as t

from exporter.database.session import AsyncSession

from .serializers import ValidatorStatistic
from .models import Validator


async def create_validator(
    session: AsyncSession,
    wallet_address: str,
    adnl_address: str,
    public_key: str
) -> Validator:
    validator = Validator(
        wallet_address=wallet_address,
        adnl_address=adnl_address,
        public_key=public_key,
    )
    session


async def get_validators() -> t.List[Validator]:
    pass


async def store_validator_stats(stats: ValidatorStatistic) -> Validator:
    async with AsyncSession() as session:
        print('Creating')
        stats = Validator(
            wallet_address=stats.wallet_address,
            adnl_address=stats.adnl_address,
            public_key=stats.public_key,
        )
        await session.add(stats)
        await session.flush()
        await session.refresh(stats)
        return stats


async def get_validator_stats_by_address(
    session: AsyncSession,
    wallet_or_adnl_address: str,
) -> Validator:
    return await session.query(Validator).where(
        (Validator.adnl_address == wallet_or_adnl_address)
        | (Validator.wallet_address == wallet_or_adnl_address)
    ).one()

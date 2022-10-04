import typing as t

from sqlalchemy.sql.expression import select

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
    session.add(validator)
    await session.flush()
    await session.refresh(validator)
    await session.commit()
    return validator


async def get_validators(session: AsyncSession) -> t.List[Validator]:
    return (
        await session.execute(
            select(Validator),
        )
    ).scalars().all()


async def store_validator_stats(
    session: AsyncSession,
    stats: ValidatorStatistic,
) -> Validator:
    print('Creating')
    created_stats = Validator(
        wallet_address=stats.wallet_address,
        adnl_address=stats.adnl_address,
        public_key=stats.public_key,
    )
    session.add(created_stats)
    await session.flush()
    await session.refresh(created_stats)
    return created_stats


async def get_validator_stats_by_address(
    session: AsyncSession,
    wallet_or_adnl_address: str,
) -> Validator:
    return await session.query(Validator).where(
        (Validator.adnl_address == wallet_or_adnl_address)
        | (Validator.wallet_address == wallet_or_adnl_address)
    ).one()

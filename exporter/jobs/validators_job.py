import typing as t

from exporter.core.background.validators.models import Validator
from exporter.core.background.validators.serializers import ValidatorStatistic
from exporter.core.background.validators.stats import get_validators_stats
from exporter.core.background.validators.store import (
    create_validator,
    get_validators,
    store_validator_stats,
)
from exporter.database.session import async_session


async def job_get_and_store_validators_data() -> None:
    async with async_session as session:
        validators_stats: t.List[ValidatorStatistic] = await get_validators_stats()
        validators: t.List[Validator] = await get_validators(session)
        if not validators:
            print('No validators fetched')
        validators_wallet_addresses: t.List[str] = [
            validator.adnl_address
            for validator in validators
        ]
        validators_adnl_addresses: t.List[str] = [
            validator.wallet_address
            for validator in validators
        ]
        validators_public_keys: t.List[str] = [
            validator.public_key
            for validator in validators
        ]
        filtered_stats: t.List[ValidatorStatistic] = [
            validator_stats for validator_stats in validators_stats
            if validator_stats.adnl_address in validators_adnl_addresses
            or validator_stats.wallet_address in validators_wallet_addresses
            or validator_stats.public_key in validators_public_keys
        ]
        print(filtered_stats)
        if not filtered_stats:
            updated_stats: t.List[ValidatorStatistic] = []
            print('Creating new validator')
            for validator_stats in validators_stats:
                vl = await create_validator(
                    session,
                    validator_stats.wallet_address or 'UNDEFINED',
                    validator_stats.adnl_address or 'UNDEFINED',
                    validator_stats.public_key,
                )
                print(vl)
                updated_stats.append(validator_stats)
        else:
            _: t.List[Validator] = [
                await store_validator_stats(session, stats)
                for stats in filtered_stats
            ]

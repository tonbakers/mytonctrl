import typing as t

from exporter.core.background.validators.models import Validator
from exporter.core.background.validators.stats import get_validators_stats
from exporter.core.background.validators.store import store_validator_stats
from exporter.core.background.validators.serializers import ValidatorStatistic
from exporter.jobs.runner import run_in_executor


@run_in_executor
async def job_get_and_store_validators_data() -> None:
    validators_stats: t.List[ValidatorStatistic] = await get_validators_stats()
    _: t.List[Validator] = [
        await store_validator_stats(stats) for stats in validators_stats
    ]

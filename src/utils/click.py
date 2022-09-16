import re

import click

from typing import Final, List, Optional


VALID_ADDRESS_REGEXP: Final[re.Pattern] = re.compile(r'[0-9A-Za-z-_/]{48}$')


def validate_address(wallet_address: str) -> bool:
    return VALID_ADDRESS_REGEXP.match(wallet_address) is not None


def comma_separated(
    _: click.Context,
    __: click.Option,
    values: str,
) -> Optional[List[str]]:
    if values is not None:
        if ',' not in values:
            return [values]
        return values.split(',')
    return values

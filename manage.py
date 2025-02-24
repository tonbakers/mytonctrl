import json
import os
import getpass

import click
import bcrypt
import requests
import yaml

import mytonctrl
import mytoncore
import mytoninstaller as installer

from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Final, List, Optional
from pathlib import Path

from pydantic.main import BaseModel
from mypylib.mypylib import MyPyClass

from src.ton.factory import get_ton_controller
from src.ton import status_messages
from src.ton.addr import build_addr, parse_base64_address
from src.utils.click import comma_separated
from src.utils.click_messages import error, message, warning
from src.utils.exceptions import BalanceIsTooLow, WalletAccountNotInitialized

main: Final[click.Group] = click.Group()

AMOUNT_MIN_VALUE: Final[int] = 0

# Disable logging
MyPyClass.AddLog = lambda *args, **kwargs: None

WALLET_TABLE: Final[str] = '''--------------------
Account status: {}
Account balance: {}
Wallet address: {}
Wallet name: {}
Wallet version: {}
Wallet work-chain: {}
--------------------'''


class FlagArguments(BaseModel):
    flags: Optional[List[str]]
    timeout: Optional[int]
    sub_wallet: Optional[str]


class WalletStatusInfoGetEnum(str, Enum):
    fast = 'fast'
    slow = 'slow'


@main.command(
    'mc',
    help='Move coins to specified account/wallet.',
)
@click.argument('wallet-name', type=click.STRING)
@click.argument('target-address', type=click.STRING)
@click.argument('amount', type=Decimal)
@click.option(
    '-f', '--flags',
    default=None,
    callback=comma_separated,
    type=click.STRING,
    help='Additional flags.',
)
@click.option(
    '-t', '--timeout',
    default=30,
    type=click.INT,
    help='Transfer timeout.',
)
@click.option(
    '-sw', '--sub-wallet',
    default=None,
    type=click.STRING,
    help='Sub-wallet to be used.',
)
def move_coins(
    wallet_name: str,
    target_address: str,
    amount: Decimal,
    flags: Optional[List[str]] = None,
    timeout: Optional[int] = None,
    sub_wallet: Optional[str] = None,
) -> None:
    keywords = FlagArguments(
        flags=flags,
        timeout=timeout,
        sub_wallet=sub_wallet,
    )
    ton_controller: mytoncore.MyTonCore = get_ton_controller()
    if wallet_name == target_address:
        raise error('Given WALLET-ADDRESS & TARGET-ADDRESS are identical.')
    if amount < AMOUNT_MIN_VALUE:
        raise error(f'Amount to transfer cannot be lower than "{AMOUNT_MIN_VALUE}"')
    try:
        source_wallet: mytoncore.Wallet = ton_controller.GetLocalWallet(wallet_name)
    except Exception as err:
        raise error(
            f'Failed to get wallet with name/address "{wallet_name}"',
            *err.args,
        )
    try:
        target_wallet: mytoncore.Wallet = ton_controller.GetDestinationAddr(target_address)
    except Exception as err:
        raise error(
            f'Failed to get wallet with name/address "{target_address}"',
            *err.args,
        )
    try:
        keywords.flags = keywords.flags or []
        ton_controller.MoveCoins(
            source_wallet,
            target_wallet,
            amount,
            **keywords.dict(),
        )
        message(f'Successfully sent coins to "{target_address}"; Sent amount: "{amount}"')
    except (BalanceIsTooLow, WalletAccountNotInitialized) as err:
        raise error(
            f'Failed to make coins transfer.',
            *err.args,
        )


@main.command(
    'wallets-list',
    help='Wallets list of your account.',
)
def wallets_list():
    ton_controller: mytoncore.MyTonCore = get_ton_controller()
    wallets: List[mytoncore.Wallet] = ton_controller.GetWallets()
    if wallets is None or not wallets:
        raise message('Not found any wallets.', exit_after=True)
    wallets_map = []
    for wallet in wallets:
        account = ton_controller.GetAccount(wallet.addrB64)
        if account.status != 'active':
            wallet.addrB64 = wallet.addrB64_init
        wallets_map.append([
            account.status,
            account.balance,
            wallet.addrB64,
            wallet.name,
            wallet.version,
            wallet.workchain,
        ])
    for wallet_info in wallets_map:
        message(WALLET_TABLE.format(*wallet_info))


@main.command(
    'status',
    help='Get wallet status information. ',
)
@click.argument(
    'status_type',
    default=WalletStatusInfoGetEnum.fast,
    type=WalletStatusInfoGetEnum,
)
def get_status(status_type: Optional[str]) -> None:
    ton_controller: mytoncore.MyTonCore = get_ton_controller()
    config34: Dict = ton_controller.GetConfig34()
    config36: Dict = ton_controller.GetConfig36()
    statistics = ton_controller.GetSettings('statistics')

    full_elector_address = ton_controller.GetFullElectorAddr()
    start_work_time = ton_controller.GetActiveElectionId(full_elector_address)
    validator_efficiency = None
    online_validators_count = 0
    if status_type != WalletStatusInfoGetEnum.fast:
        online_validators: Optional[List[Dict]] = ton_controller.GetOnlineValidators()
        validator_efficiency = ton_controller.GetValidatorEfficiency()
        if online_validators is not None:
            online_validators_count = len(online_validators)
    
    total_validators = config34['totalValidators']
    shards_count = ton_controller.GetShardsNumber()
    offers_count: Dict[str, int] = ton_controller.GetOffersNumber()
    complaints_count: Dict[str, int] = ton_controller.GetComplaintsNumber()
    tx_per_second_average = ton_controller.GetStatistics('tpsAvg', statistics)
    message(
        status_messages.build_status_message(
            start_work_time,
            online_validators_count,
            total_validators,
            shards_count,
            offers_count,
            complaints_count,
            tx_per_second_average,
        ),
    )

    adnl_address: str = ton_controller.GetAdnlAddr()
    validator_index: int = ton_controller.GetValidatorIndex()
    validator_wallet: mytonctrl.Wallet = ton_controller.GetValidatorWallet()
    validator_status = ton_controller.GetValidatorStatus()
    database_size = ton_controller.GetDbSize()
    database_usage = ton_controller.GetDbUsage()
    memory_info = mytoncore.GetMemoryInfo()
    swap_info = mytoncore.GetSwapInfo()
    network_load_average = ton_controller.GetStatistics('netLoadAvg', statistics)
    disks_load_average = ton_controller.GetStatistics('disksLoadAvg', statistics)
    disks_load_percent_average = ton_controller.GetStatistics('disksLoadPercentAvg', statistics)
    message(
        status_messages.build_local_validator_status_message(
            adnl_address,
            validator_index,
            validator_efficiency,
            validator_wallet,
            ton_controller.GetAccount(validator_wallet.addrB64) if validator_wallet is not None else None,
            validator_status,
            database_size,
            database_usage,
            memory_info,
            swap_info,
            network_load_average,
            disks_load_average,
            disks_load_percent_average,
        ),
    )

    full_config_address = ton_controller.GetFullConfigAddr()
    config15 = ton_controller.GetConfig15()
    config17 = ton_controller.GetConfig17()
    message(
        status_messages.build_network_configuration_message(
            full_config_address,
            full_elector_address,
            config15,
            config17,
        )
    )
    
    root_work_chain_enabled_time: int = ton_controller.GetRootWorkchainEnabledTime()
    old_start_work_time = config36.get('startWorkTime', config34.get('startWorkTime'))
    raise message(
        status_messages.build_ton_timestamps_message(
            root_work_chain_enabled_time,
            start_work_time,
            old_start_work_time,
            config15,
        ),
        exit_after=True,
    )


@main.command(
    'get',
    help='Get network settings.',
)
@click.argument(
    'name',
    required=True,
    type=click.STRING,
)
def get_settings(name: str) -> None:
    ton_controller: mytoncore.MyTonCore = get_ton_controller()
    value = ton_controller.GetSettings(name)
    raise message(
        f'Settings:',
        f'{name} = {value}',
        exit_after=True,
    )


@main.command(
    'set',
    help='Set network settings.',
)
@click.argument(
    'name',
    required=True,
    type=click.STRING,
)
@click.argument(
    'value',
    required=True,
)
def set_settings(name: str, value: Any) -> None:
    ton_controller: mytoncore.MyTonCore = get_ton_controller()
    ton_controller.SetSettings(name, value)
    value = ton_controller.GetSettings(name)
    raise message(
        'Successfully set setting:',
        f'{name} = {value}',
        exit_after=True,
    )


@main.command(
    help='Vote offer. Type comma separated. Ex: <offer-hash-1>,<offer-hash-2>',
)
@click.argument(
    'offer-hashes',
    required=True,
    type=click.STRING,
    callback=comma_separated,
)
def vote(offer_hashes: str):
    ton_controller: mytoncore.MyTonCore = get_ton_controller()
    applied_offers: List[str] = []
    for offer_hash in offer_hashes:
        try:
            ton_controller.VoteOffer(int(offer_hash))
            applied_offers.append(offer_hash)
        except ValueError as err:
            warning(
                f'Offer-hash with value "{offer_hash}" is skipped due:',
                *err.args,
            )
            continue
        except Exception as err:
            warning(
                f'Offer-hash with value "{offer_hash}" is skipped due:',
                *err.args,
            )
            continue
    if applied_offers:
        raise message(
            'Successfully applied offers:',
            ', '.join(applied_offers),
            exit_after=True,
        )
    else:
        raise message('Not offers was applied!', exit_after=True)


@main.command(
    help='Update "mytonctrl" to actual version',
)
@click.argument(
    'URL',
    type=click.STRING,
    default=None,
    required=False,
)
@click.argument(
    'BRANCH',
    type=click.STRING,
    default=None,
    required=False,
)
def update(url: str, branch: str) -> None:
    # Patching base exit to use custom
    mytonctrl.local.Exit = lambda: None
    try:
        mytonctrl.Update((url, branch))
    except Exception as err:
        raise error(
            'Failed to update "mytonctrl" due errors:',
            *err.args,
        )
    raise message('Successfully updated!', exit_after=True)


@main.command(
    help='Upgrade TON sources to the latest version. Will re-compile existing binaries.',
)
@click.argument(
    'URL',
    type=click.STRING,
    default=None,
)
@click.argument(
    'BRANCH',
    type=click.STRING,
    default=None,
)
def upgrade(url: str, branch: str) -> None:
    try:
        mytonctrl.Upgrade((url, branch))
    except Exception as err:
        raise error(
            'Failed to upgrade TON sources due errors:',
            *err.args,
        )
    raise message('Successfully upgraded!', exit_after=True)


@main.command(
    'create-config',
    help='Generates config for local validator.'
)
@click.option(
    '--path',
    default='/usr/bin/ton/local.config.json',
    type=click.STRING,
    required=False,
    help='Path where config must be created.',
)
@click.option(
    '--config-path',
    default='/usr/bin/ton/global.config.json',
    type=click.STRING,
    required=False,
    help='Global config path, if file is not exists, '
         'will try to request from "ton.org"',
)
@click.option(
    '--config-ton-http-api',
    default=None,
    type=click.STRING,
    required=False,
)
@click.option(
    '--config-url',
    default='https://ton.org/global-config.json',
    type=click.STRING,
    required=False,
    help='Global config URL if want to download latest version '
         'or file of global config not found.',
)
def get_config(
    path: Optional[str],
    config_path: Optional[str],
    config_ton_http_api: Optional[str],
    config_url: Optional[str],
) -> None:
    message('Creating config file based on local validator.')
    init_config_path: str = config_path or '/usr/bin/ton/global.config.json'
    create_config_path: str = path or '/usr/bin/ton/local.config.json'
    installer.Init()
    try:
        message(f'Reading GLOBAL config from: "{init_config_path}"')
        with open(init_config_path, 'r+') as ton_config:
            ton_configuration: Dict[str, Any] = json.load(ton_config)

    except FileNotFoundError as err:
        error(
            f'Configuration of TON blockchain not found on your drive at: "{init_config_path}".',
            *err.args[1:],
            'Will try to download configuration from official TON site.',
        )
        response = requests.get(config_url)
        if response.status_code != 200:
            raise error('Failed to get response from official TON site.')
        ton_configuration: Dict[str, Any] = response.json()
        with open(init_config_path, 'w+') as missing_config_file:
            json.dump(ton_configuration, missing_config_file, indent=4)
    try:
        message(f'Creating LOCAL config at: "{create_config_path}"')
        with open(create_config_path, 'w+') as local_config:
            init_block = installer.GetInitBlock()
            lite_server_config = installer.GetLiteServerConfig()
            ton_configuration['liteservers'] = [lite_server_config]
            ton_configuration["validator"]["init_block"]["seqno"] = init_block["seqno"]
            ton_configuration["validator"]["init_block"]["root_hash"] = mytoncore.hex2base64(init_block["rootHash"])
            ton_configuration["validator"]["init_block"]["file_hash"] = mytoncore.hex2base64(init_block["fileHash"])
            json.dump(ton_configuration, local_config, indent=4)
    except FileNotFoundError as err:
        raise error(
            f'TON configuration file not found on path "{init_config_path}".',
            *err.args[1:],
        )
    except KeyError as err:
        raise error(
            'Failed to get configuration key for:',
            *err.args,
        )
    except Exception as err:
        raise error(
            'Failed to create config based on validator.',
            *err.args,
        )
    if config_ton_http_api is not None:
        file_path = Path(os.getcwd()) / Path(local_config.name)
        if not file_path.exists():
            os.system(f'cp {file_path} {create_config_path}')
        else:
            os.system(f'cp {file_path} {config_ton_http_api}')
    raise message(f'Created config-file on path: "{create_config_path}"', exit_after=True)


@main.command(
    'add-prom-user',
    help='Command to give user access to the Prometheus web interface.',
)
@click.argument(
    'USERNAME',
    type=click.STRING,
    required=True,
)
@click.option(
    '--config-path',
    default='./prometheus-web-config.yml',
    type=click.STRING,
)
def add_prometheus_user(username: str, config_path: str) -> None:
    message('Type your password which be used to access web interface.')
    password: str = getpass.getpass('Password: ')
    hashed_password: str = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with open(config_path, 'r') as file:
            data: Dict[str, Any] = yaml.load(file, yaml.Loader)
    except FileNotFoundError as err:
        raise error(
            f'Config file with path "{config_path}" is not found!',
            *err.args,
        )
    data['basic_auth_users'].update({username: hashed_password})
    with open(config_path, 'w') as file:
        yaml.dump(data, stream=file, Dumper=yaml.Dumper)
    raise message(f'Successfully set password for user "{username}".', exit_after=True)


@main.command(
    'write-addr',
    help='Method to creating *.addr files from short address notation.',
)
@click.argument(
    'ADDRESS',
    type=click.STRING,
    required=True,
)
@click.argument(
    'FILE_PATH',
    type=click.STRING,
    required=True,
)
@click.option(
    '-f', '--is-full',
    default=False,
    is_flag=True,
    help='Use short or usual TON address.',
)
@click.option(
    '-n', '--negative-work-chain',
    default=False,
    is_flag=True,
    help='"Click" cannot parse signed integers from cli, so to send "-1" work-chain '
         'use this flag.',
)
def write_to_addr_file(
    address: str,
    file_path: str,
    negative_work_chain: bool,
    is_full: bool,
) -> None:
    if is_full is True:
        try:
            workchain, address = address.split(':')
        except ValueError:
            raise error(
                'Passed invalid raw address. '
                'Accepted scheme only is: "workchain(int):hexadecimal_address(str)"',
            )
        address: str
        workchain: int = int(workchain)
        if negative_work_chain is True:
            workchain = -workchain
        message(
            'Using address & work-chain to generate *.addr file:',
            f'Workchain: {workchain}',
            f'Address: {address}'
        )
        byte_address = build_addr(address, workchain)
        with open(file_path, 'wb') as file:
            file.write(byte_address)
        path = f'{os.getcwd()}' / Path(file_path)
        raise message(
            f'Successfully created *.addr file at: "{path}"',
            exit_after=True,
        )

    workchain, full_address, bounceable, crc_failed = parse_base64_address(address)
    if crc_failed is True:
        warning('CRC checksum validation failed!')
    built_addr = build_addr(full_address, workchain)
    with open(file_path, 'wb') as file:
        file.write(built_addr)
        path = f'{os.getcwd()}' / Path(file_path)
        message(f'Successfully created *.addr file at: "{path}"')
    raise message(
        'Decoded short address data: ',
        f'work-chain: {workchain}',
        f'full-address: {full_address}',
        f'bounceable: {bounceable}',
        exit_after=True,
    )


@main.command(
    'use-tha',
    help='Command to install or start using "ton-http-api"',
)
def use_ton_http_api() -> None:
    ton_http_api_path = Path('/etc/systemd/system/ton-http-api.service')
    if ton_http_api_path.exists():
        raise message(
            '"ton-http-api" unit already exists. Use following commands to run '
            'or get status:',
            'systemctl start ton-http-api',
            'systemctl status ton-http-api',
            exit_after=True,
        )
    else:
        warning(
            '"ton-http-api" service not found in "systemd" units. '
            'Starting installation.',
        )
        installer.enable_ton_http_api()
    raise message('Successfully installed and started "ton-http-api"', exit_after=True)


if __name__ == '__main__':
    main()

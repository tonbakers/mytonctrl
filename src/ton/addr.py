import base64

import crc16

from typing import Tuple


def build_addr(address: str, workchain: int) -> bytes:
    byte_address: bytes = bytes.fromhex(address)
    # TODO: Research this trick with workchain -1 == 255
    # TODO: Need to add 4 buffer bytes to use struct.unpack
    byte_workchain: bytes = int.to_bytes(workchain // 256, 4, 'big', signed=True)
    return byte_address + byte_workchain


def parse_base64_address(address: str) -> Tuple[int, str, bool, bool]:
    crc_failed = False
    address: str = make_base64_replacements(address)
    byte_address: bytes = address.encode()
    decoded_address: bytes = base64.b64decode(byte_address)
    if check_crc_checksum(decoded_address) is False:
        crc_failed = True
    # TODO: Research this trick with workchain -1 == 255
    workchain: int = -(int.from_bytes(decoded_address[1:2], 'big') % 254)
    full_address: str = decoded_address[2:34].hex()
    is_bounceable = (decoded_address[0] & 0x40) != 0
    return workchain, full_address, is_bounceable, crc_failed


def check_crc_checksum(byte_address: bytes) -> bool:
    # TODO: Need to implement using of classic python crc lib
    crc_bytes = byte_address[34:36]
    crc_data = bytes(byte_address[:34])
    current_checksum = int.from_bytes(crc_bytes, 'big')
    expected_checksum = crc16.crc16xmodem(crc_data)
    return current_checksum == expected_checksum


def build_crc_checksum(byte_address: bytes) -> int:
    return crc16.crc16xmodem(byte_address)


def make_base64_replacements(string: str) -> str:
    for replacements in [('-', '+'), ('_', '/')]:
        string = string.replace(*replacements)
    return string

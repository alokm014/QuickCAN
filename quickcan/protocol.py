from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import IntEnum

from quickcan.utils.helpers import checksum, escape_data, unescape_data

START_BYTE = 0xAA
ESCAPE_BYTE = 0xAB
PROTOCOL_VERSION = 0x01

__all__ = [
    "CANFrame", "Command", "encode_frame", "decode_frame",
    "START_BYTE", "ESCAPE_BYTE", "PROTOCOL_VERSION"
]

# --- Command Types ---
class Command(IntEnum):
    CAN_SEND        = 0x01
    HEARTBEAT       = 0x02
    ACK             = 0x03
    NACK            = 0x04
    DEVICE_INFO     = 0x10
    PING            = 0x20
    CONFIG_GET      = 0x30
    CONFIG_SET      = 0x31
    RESET           = 0x40
    SET_FILTER      = 0x41
    CLEAR_FILTER    = 0x42


@dataclass
class CANFrame:
    can_id: int
    data: List[int]
    extended: bool = False
    flags: int = 0
    timestamp: float = 0.0


def encode_frame(frame: CANFrame, cmd: Command = Command.CAN_SEND) -> bytes:
    dlc = len(frame.data)
    flags = dlc & 0x0F
    if frame.extended:
        flags |= 0x80

    payload = bytearray([
        PROTOCOL_VERSION,
        cmd,
        (frame.can_id >> 24) & 0xFF,
        (frame.can_id >> 16) & 0xFF,
        (frame.can_id >> 8) & 0xFF,
        frame.can_id & 0xFF,
        flags
    ])
    payload.extend(frame.data)
    payload.append(checksum(payload))

    return bytes([START_BYTE]) + escape_data(payload)


def decode_frame(buf: bytes) -> Optional[Tuple[Command, CANFrame]]:
    if not buf or buf[0] != START_BYTE:
        return None

    try:
        payload = unescape_data(buf[1:])
        if len(payload) < 8:
            return None

        version = payload[0]
        if version != PROTOCOL_VERSION:
            return None

        cmd = Command(payload[1])
        can_id = (payload[2] << 24) | (payload[3] << 16) | (payload[4] << 8) | payload[5]
        flags = payload[6]
        dlc = flags & 0x0F
        data = list(payload[7:7 + dlc])

        if checksum(payload[:-1]) != payload[-1]:
            return None

        frame = CANFrame(
            can_id=can_id,
            data=data,
            extended=bool(flags & 0x80),
            flags=flags
        )
        return cmd, frame

    except Exception:
        return None

# protocol.py
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Protocol constants
START_BYTE = 0xAA
ESCAPE_BYTE = 0xAB
PROTOCOL_VERSION = 0x01

# Command types
CMD_CAN_SEND = 0x01
CMD_HEARTBEAT = 0x02
CMD_ACK = 0x03

@dataclass
class CANFrame:
    can_id: int
    data: List[int]
    extended: bool = False
    flags: int = 0
    timestamp: float = 0.0  # Optional, can be set at receiver side

# --- Helper Functions ---

def checksum(data: bytes) -> int:
    """Compute simple additive checksum over data."""
    return sum(data) % 256

def escape_data(data: bytes) -> bytes:
    """Escape START_BYTE and ESCAPE_BYTE using simple XOR masking."""
    escaped = bytearray()
    for b in data:
        if b in (START_BYTE, ESCAPE_BYTE):
            escaped.append(ESCAPE_BYTE)
            escaped.append(b ^ 0x20)
        else:
            escaped.append(b)
    return bytes(escaped)

def unescape_data(data: bytes) -> bytes:
    """Decode escaped data stream."""
    result = bytearray()
    it = iter(data)
    for b in it:
        if b == ESCAPE_BYTE:
            next_byte = next(it, None)
            if next_byte is None:
                break  # Broken escape sequence
            result.append(next_byte ^ 0x20)
        else:
            result.append(b)
    return bytes(result)

# --- Frame Encoder / Decoder ---

def encode_frame(frame: CANFrame, cmd: int = CMD_CAN_SEND) -> bytes:
    """Encodes a CANFrame into the binary protocol."""
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

def decode_frame(buf: bytes) -> Optional[Tuple[int, CANFrame]]:
    """Decodes a full frame byte stream into a (cmd, CANFrame) tuple."""
    if not buf or buf[0] != START_BYTE:
        return None

    try:
        payload = unescape_data(buf[1:])
        if len(payload) < 8:
            return None

        version = payload[0]
        if version != PROTOCOL_VERSION:
            return None

        cmd = payload[1]
        can_id = (payload[2] << 24) | (payload[3] << 16) | (payload[4] << 8) | payload[5]
        flags = payload[6]
        dlc = flags & 0x0F

        if len(payload) < 7 + dlc + 1:
            return None

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

# --- Streaming Frame Rebuilder ---

class FrameStreamDecoder:
    """Used to reassemble bytes into full QuickCAN frames from a raw byte stream."""
    def __init__(self):
        self.buffer = bytearray()
        self.in_frame = False

    def feed(self, byte_in: int) -> Optional[bytes]:
        """Feed one byte at a time. Returns a complete frame when available."""
        if byte_in == START_BYTE:
            if self.in_frame and self.buffer:
                old_frame = bytes([START_BYTE]) + self.buffer
                self.buffer = bytearray()
                return old_frame
            self.in_frame = True
            self.buffer = bytearray()
            return None
        elif self.in_frame:
            self.buffer.append(byte_in)
        return None

    def flush(self) -> Optional[bytes]:
        """Force return of current buffer (if not empty)."""
        if self.buffer:
            return bytes([START_BYTE]) + self.buffer
        return None

# Utils: Checksums, timestamps, etc.
# quickcan/utils/helpers.py

def checksum(data: bytes) -> int:
    return sum(data) % 256

def escape_data(data: bytes) -> bytes:
    escaped = bytearray()
    for b in data:
        if b in (0xAA, 0xAB):
            escaped.append(0xAB)
            escaped.append(b ^ 0x20)
        else:
            escaped.append(b)
    return bytes(escaped)

def unescape_data(data: bytes) -> bytes:
    result = bytearray()
    it = iter(data)
    for b in it:
        if b == 0xAB:
            next_byte = next(it, None)
            if next_byte is None:
                break
            result.append(next_byte ^ 0x20)
        else:
            result.append(b)
    return bytes(result)

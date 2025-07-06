# Transport: Serial/USB abstraction
# quickcan/transport/stream_decoder.py
class FrameStreamDecoder:
    def __init__(self):
        self.buffer = bytearray()
        self.in_frame = False

    def feed(self, byte_in: int):
        if byte_in == 0xAA:
            if self.in_frame and self.buffer:
                full_frame = bytes([0xAA] + list(self.buffer))
                self.buffer.clear()
                return full_frame
            self.in_frame = True
            self.buffer.clear()
            return None
        elif self.in_frame:
            self.buffer.append(byte_in)
        return None

    def flush(self):
        if self.buffer:
            return bytes([0xAA] + list(self.buffer))
        return None
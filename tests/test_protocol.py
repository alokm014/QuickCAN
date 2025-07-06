import unittest
from quickcan.protocol import (
    CANFrame, encode_frame, decode_frame, Command,
    START_BYTE, ESCAPE_BYTE
)
from quickcan.transport.stream_decoder import FrameStreamDecoder
from quickcan.utils.helpers import escape_data, unescape_data

class TestProtocol(unittest.TestCase):

    def test_basic_encode_decode(self):
        frame = CANFrame(can_id=0x123, data=[0x11, 0x22, 0x33])
        raw = encode_frame(frame)
        self.assertEqual(raw[0], START_BYTE)

        result = decode_frame(raw)
        self.assertIsNotNone(result)
        cmd, decoded = result
        self.assertEqual(cmd, Command.CAN_SEND)
        self.assertEqual(decoded.can_id, frame.can_id)
        self.assertEqual(decoded.data, frame.data)

    def test_extended_id(self):
        frame = CANFrame(can_id=0x1ABCDE12, data=[0xFF], extended=True)
        raw = encode_frame(frame)
        result = decode_frame(raw)
        self.assertIsNotNone(result)
        cmd, decoded = result
        self.assertTrue(decoded.extended)
        self.assertEqual(decoded.can_id, frame.can_id)

    def test_checksum_validation(self):
        frame = CANFrame(0x101, [0x01, 0x02])
        encoded = bytearray(encode_frame(frame))
        encoded[-1] ^= 0x01  # Corrupt checksum
        self.assertIsNone(decode_frame(bytes(encoded)))

    def test_escape_unescape_roundtrip(self):
        original = bytes([START_BYTE, ESCAPE_BYTE, 0x01])
        escaped = escape_data(original)
        unescaped = unescape_data(escaped)
        self.assertEqual(original, unescaped)

    def test_empty_data(self):
        frame = CANFrame(0x321, [])
        raw = encode_frame(frame)
        result = decode_frame(raw)
        self.assertIsNotNone(result)
        cmd, decoded = result
        self.assertEqual(decoded.data, [])

    def test_invalid_start_byte(self):
        self.assertIsNone(decode_frame(bytes([0x00, 0x01, 0x02])))

    def test_incomplete_frame(self):
        self.assertIsNone(decode_frame(bytes([START_BYTE, 0x01, 0x02])))

    def test_bad_escape_sequence(self):
        corrupted = bytes([START_BYTE, 0x01, ESCAPE_BYTE])
        result = decode_frame(corrupted)
        self.assertIsNone(result)

    def test_stream_decoder_single_frame(self):
        decoder = FrameStreamDecoder()
        frame = CANFrame(0x123, [0x01, 0x02])
        raw = encode_frame(frame)

        for b in raw:
            decoder.feed(b)

        result = decoder.flush()
        self.assertIsNotNone(result)
        cmd, decoded = decode_frame(result)
        self.assertEqual(decoded.can_id, 0x123)

    def test_stream_decoder_multiple_frames(self):
        decoder = FrameStreamDecoder()
        f1 = encode_frame(CANFrame(0x100, [0x01]))
        f2 = encode_frame(CANFrame(0x200, [0x02]))

        raw_stream = f1 + f2
        found = []

        for b in raw_stream:
            res = decoder.feed(b)
            if res:
                found.append(res)

        found.append(decoder.flush())
        decoded_ids = [decode_frame(f)[1].can_id for f in found if decode_frame(f)]
        self.assertIn(0x100, decoded_ids)
        self.assertIn(0x200, decoded_ids)

    def test_invalid_version(self):
        frame = CANFrame(0x100, [0x01])
        raw = bytearray(encode_frame(frame))
        raw[0] = 0x01  # break start byte
        raw[1] ^= 0x01  # corrupt version
        self.assertIsNone(decode_frame(bytes(raw)))

    def test_flush_empty_stream(self):
        decoder = FrameStreamDecoder()
        self.assertIsNone(decoder.flush())

    def test_broken_escape_sequence_in_stream(self):
        decoder = FrameStreamDecoder()
        raw = bytes([START_BYTE, 0x01, ESCAPE_BYTE])
        decoder.feed(raw[0])
        for b in raw[1:]:
            decoder.feed(b)
        result = decoder.flush()
        self.assertIsNone(decode_frame(result))


if __name__ == '__main__':
    unittest.main()

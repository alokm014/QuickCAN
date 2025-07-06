# Test: Driver interactions
import pytest
from unittest.mock import MagicMock, patch
from quickcan.driver import QuickCAN
from quickcan.protocol import CANFrame, Command, encode_frame

@pytest.fixture
def mock_serial():
    with patch("quickcan.driver.serial.Serial") as mock:
        instance = mock.return_value
        instance.in_waiting = 0
        yield instance

def test_send_can_frame(mock_serial):
    driver = QuickCAN(port="COM1")
    driver.send(0x123, [0x01, 0x02, 0x03])
    assert mock_serial.write.called
    driver.close()

def test_send_all_commands(mock_serial):
    driver = QuickCAN(port="COM1")

    driver.send_heartbeat()
    driver.send_ack()
    driver.send_nack()
    driver.send_device_info_request()
    driver.send_ping()
    driver.send_config_get(0x01)
    driver.send_config_set(0x02, [0x10, 0x20])

    assert mock_serial.write.call_count == 7
    driver.close()

@patch("quickcan.driver.serial.Serial")
def test_receive_valid_frame(mock_serial_cls):
    from quickcan.protocol import CANFrame, encode_frame, Command

    frame = CANFrame(can_id=0x123, data=[0x01, 0x02])
    raw_bytes = encode_frame(frame, cmd=Command.CAN_SEND)

    mock_serial = MagicMock()
    mock_serial.in_waiting = len(raw_bytes)

    def fake_read():
        for b in raw_bytes:
            yield bytes([b])
        while True:
            yield b''

    mock_serial.read = MagicMock(side_effect=fake_read())
    mock_serial_cls.return_value = mock_serial

    received = []

    def callback(cmd, f):
        received.append((cmd, f))

    driver = QuickCAN(port="COM1")
    driver.set_receive_callback(callback)
    driver.receive()

    assert len(received) == 1
    assert received[0][0] == Command.CAN_SEND
    assert received[0][1].can_id == 0x123
    assert received[0][1].data == [0x01, 0x02]
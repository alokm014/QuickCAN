# quickcan/driver.py

import serial
import logging
from typing import Callable

from quickcan.protocol import encode_frame, decode_frame, CANFrame, Command
from quickcan.transport.stream_decoder import FrameStreamDecoder

logger = logging.getLogger(__name__)

class QuickCAN:
    def __init__(self, port: str, baudrate: int = 115200):
        self.serial = serial.Serial(port, baudrate, timeout=0.1)
        self.callback: Callable[[Command, CANFrame], None] = None
        self.decoder = FrameStreamDecoder()
        logger.info(f"QuickCAN initialized on port {port} @ {baudrate} bps")

    def set_receive_callback(self, callback: Callable[[Command, CANFrame], None]):
        """Register callback for incoming frames"""
        self.callback = callback
        logger.debug("Receive callback set")

    def send(self, can_id: int, data: list[int], extended: bool = False):
        """Send standard CAN frame (CMD_CAN_SEND)"""
        frame = CANFrame(can_id=can_id, data=data, extended=extended)
        packet = encode_frame(frame, cmd=Command.CAN_SEND)
        self.serial.write(packet)
        logger.info(f"Sent CAN frame: ID=0x{can_id:X}, Data={data}, Extended={extended}")

    def receive(self):
        """Poll and decode frames from serial"""
        while self.serial.in_waiting:
            byte = self.serial.read(1)
            if not byte:
                continue  # Skip empty reads
            result = self.decoder.feed(byte[0])
            if result:
                decoded = decode_frame(result)
                if decoded and self.callback:
                    cmd, frame = decoded
                    self.callback(cmd, frame)

    # --- Command-Specific Send Helpers ---

    def send_heartbeat(self):
        self._send_simple_command(Command.HEARTBEAT)

    def send_ack(self):
        self._send_simple_command(Command.ACK)

    def send_nack(self):
        self._send_simple_command(Command.NACK)

    def send_device_info_request(self):
        self._send_simple_command(Command.DEVICE_INFO)

    def send_ping(self):
        self._send_simple_command(Command.PING)

    def send_config_get(self, key_id: int):
        frame = CANFrame(0x00, [key_id])
        packet = encode_frame(frame, cmd=Command.CONFIG_GET)
        self.serial.write(packet)
        logger.info(f"Sent CONFIG_GET for key_id={key_id}")

    def send_config_set(self, key_id: int, values: list[int]):
        frame = CANFrame(0x00, [key_id] + values)
        packet = encode_frame(frame, cmd=Command.CONFIG_SET)
        self.serial.write(packet)
        logger.info(f"Sent CONFIG_SET: key_id={key_id}, values={values}")

    def _send_simple_command(self, cmd: Command):
        """Helper for sending command-only frames"""
        frame = CANFrame(0x00, [])
        packet = encode_frame(frame, cmd=cmd)
        self.serial.write(packet)
        logger.info(f"Sent command: {cmd.name} (0x{cmd:02X})")

    def close(self):
        self.serial.close()
        logger.info("Serial port closed")

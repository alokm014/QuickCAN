# Driver: Serial connection and high-level control
import serial
import threading
import time
from quickcan.protocol import CANFrame, encode_frame, decode_frame

class QuickCAN:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=0.05)
        self.callback = None
        self._rx_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._running = True
        self._rx_thread.start()

    def send(self, can_id, data, extended=False):
        """Send a CAN frame over serial using QuickCAN protocol"""
        frame = CANFrame(can_id=can_id, data=data, extended=extended)
        packet = encode_frame(frame)
        self.ser.write(packet)

    def set_receive_callback(self, callback_fn):
        """Assign a callback function for received CAN frames"""
        self.callback = callback_fn

    def _receive_loop(self):
        """Continuously read from serial and decode frames"""
        buffer = bytearray()
        while self._running:
            if self.ser.in_waiting:
                byte = self.ser.read(1)
                if byte:
                    buffer.append(byte[0])

                    # Minimum size: 9 bytes
                    if len(buffer) >= 9 and buffer[0] == 0xAA:
                        frame = decode_frame(buffer)
                        if frame:
                            frame.timestamp = time.time() * 1000  # Add receive timestamp
                            if self.callback:
                                self.callback(frame)
                            buffer.clear()
            else:
                time.sleep(0.01)

    def close(self):
        self._running = False
        self.ser.close()

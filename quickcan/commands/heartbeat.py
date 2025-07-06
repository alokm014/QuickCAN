# Commands: Set bitrate, reset, filters, etc.
# quickcan/commands/heartbeat.py

import time
from quickcan.protocol import CANFrame, CMD_HEARTBEAT, encode_frame

def build_heartbeat_frame(counter: int = 0) -> bytes:
    """
    Build a heartbeat frame with an incrementing counter (optional).
    The frame doesn't carry CAN ID meaning; it's a protocol command.
    """
    frame = CANFrame(
        can_id=0x00000000,  # You may choose any reserved ID (e.g., 0x7FF or 0x0)
        data=[counter & 0xFF],
        extended=False
    )
    return encode_frame(frame, cmd=CMD_HEARTBEAT)

def send_heartbeat(serial_port, interval=1.0):
    """
    Continuously send heartbeat packets every `interval` seconds.
    `serial_port` must be an open pyserial Serial instance.
    """
    counter = 0
    try:
        while True:
            packet = build_heartbeat_frame(counter)
            serial_port.write(packet)
            print(f"💓 Sent heartbeat #{counter}")
            counter = (counter + 1) % 256
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Heartbeat sending stopped.")

# examples/test_commands.py

from quickcan.driver import QuickCAN
from quickcan.protocol import Command
import time

def on_receive(cmd, frame):
    print(f"📥 Received → CMD: 0x{cmd:02X}, ID: 0x{frame.can_id:X}, Data: {frame.data}, Extended: {frame.extended}")

def main():
    can = QuickCAN(port='COM5')  # Change COM5 to your port
    can.set_receive_callback(on_receive)

    # Send all supported commands
    can.send(can_id=0x123, data=[0x11, 0x22, 0x33])  # CAN_SEND
    can.send_heartbeat()
    can.send_ack()
    can.send_nack()
    can.send_device_info_request()
    can.send_ping()
    can.send_config_get(key_id=0x01)
    can.send_config_set(key_id=0x01, values=[0x55, 0x66])

    # Wait to receive responses
    print("📡 Listening for responses for 5 seconds...")
    for _ in range(50):
        can.receive()
        time.sleep(0.1)

    can.close()

if __name__ == '__main__':
    main()

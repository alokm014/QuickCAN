# cli/quickcan_cli.py

import argparse
from quickcan.driver import QuickCAN
from quickcan.protocol import Command

def on_receive(cmd, frame):
    print(f"\n📥 Received:")
    print(f"  Command    : {cmd.name} (0x{cmd.value:02X})")
    print(f"  CAN ID     : 0x{frame.can_id:X}")
    print(f"  Data       : {frame.data}")
    print(f"  Extended ID: {frame.extended}")

def main():
    parser = argparse.ArgumentParser(description="QuickCAN CLI Tool")
    parser.add_argument('--port', required=True, help="Serial port (e.g., COM3 or /dev/ttyUSB0)")
    
    parser.add_argument('--send', nargs='+', help="Send CAN frame: ID [DATA_BYTES...]")
    parser.add_argument('--recv', action='store_true', help="Receive mode")

    # Extra commands
    parser.add_argument('--heartbeat', action='store_true', help="Send heartbeat frame")
    parser.add_argument('--ack', action='store_true', help="Send ACK")
    parser.add_argument('--nack', action='store_true', help="Send NACK")
    parser.add_argument('--ping', action='store_true', help="Send ping")
    parser.add_argument('--device-info', action='store_true', help="Request device info")
    parser.add_argument('--config-get', type=int, help="Get config for key ID")
    parser.add_argument('--config-set', nargs='+', help="Set config: KEY_ID VALUE1 [VALUE2 ...]")

    args = parser.parse_args()

    can = QuickCAN(args.port)
    can.set_receive_callback(on_receive)

    # Command mode
    if args.send:
        can_id = int(args.send[0], 16 if args.send[0].startswith("0x") else 10)
        data = [int(b, 16) for b in args.send[1:]]
        can.send(can_id, data)
        print(f"✅ Sent CAN frame: ID=0x{can_id:X}, Data={data}")

    if args.heartbeat:
        can.send_heartbeat()
        print("✅ Sent HEARTBEAT")

    if args.ack:
        can.send_ack()
        print("✅ Sent ACK")

    if args.nack:
        can.send_nack()
        print("✅ Sent NACK")

    if args.ping:
        can.send_ping()
        print("✅ Sent PING")

    if args.device_info:
        can.send_device_info_request()
        print("✅ Sent DEVICE INFO REQUEST")

    if args.config_get is not None:
        can.send_config_get(args.config_get)
        print(f"✅ Sent CONFIG GET: key={args.config_get}")

    if args.config_set:
        key_id = int(args.config_set[0])
        values = [int(v, 16 if v.startswith("0x") else 10) for v in args.config_set[1:]]
        can.send_config_set(key_id, values)
        print(f"✅ Sent CONFIG SET: key={key_id}, values={values}")

    # Listen for incoming frames
    if args.recv:
        print("🔍 Listening for CAN frames. Press Ctrl+C to exit.")
        try:
            while True:
                can.receive()
        except KeyboardInterrupt:
            print("\n👋 Exiting...")

    can.close()

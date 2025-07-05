import argparse
from quickcan.driver import QuickCAN

def on_receive(frame):
    print(f"RX: ID=0x{frame.can_id:X}, Data={frame.data}, Extended={frame.extended}")

def main():
    parser = argparse.ArgumentParser(description="QuickCAN CLI Tool")
    parser.add_argument('--port', required=True, help="Serial port (e.g., COM3 or /dev/ttyUSB0)")
    parser.add_argument('--send', nargs='+', help="Send CAN frame: ID [DATA_BYTES...]")
    parser.add_argument('--recv', action='store_true', help="Receive mode")

    args = parser.parse_args()
    can = QuickCAN(args.port)
    can.set_receive_callback(on_receive)

    if args.send:
        can_id = int(args.send[0], 16 if args.send[0].startswith("0x") else 10)
        data = [int(b, 16) for b in args.send[1:]]
        can.send(can_id, data)
        print(f"Sent: ID=0x{can_id:X}, Data={data}")

    if args.recv:
        print("Listening for CAN frames. Press Ctrl+C to exit.")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Exiting...")

    can.close()

if __name__ == '__main__':
    main()

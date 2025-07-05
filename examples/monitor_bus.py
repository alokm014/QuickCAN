import can

def main():
    print("🔌 Connecting to QuickCAN backend...")

    # Make sure COM port is correct (e.g., "COM5" on Windows or "/dev/ttyUSB0" on Linux)
    bus = can.Bus(interface='quickcan', channel='COM5')

    print("🟢 Listening for CAN frames via QuickCAN...\n(Press Ctrl+C to stop)\n")
    try:
        while True:
            msg = bus.recv(timeout=1.0)
            if msg:
                print(f"📥 ID: 0x{msg.arbitration_id:X} | Data: {list(msg.data)} | Ext: {msg.is_extended_id}")
    except KeyboardInterrupt:
        print("\n🔴 Stopped by user.")
    finally:
        bus.shutdown()

if __name__ == "__main__":
    main()

import can
import time

def main():
    bus = can.Bus(interface='quickcan', channel='COM5')

    # Send a test message
   # message = can.Message(arbitration_id=0x321, data=[0xDE, 0xAD, 0xBE, 0xEF], is_extended_id=False)
   # bus.send(message)
   # print("✅ Test message sent.")

    # Try to receive a message for 5 seconds
    print("🔁 Waiting for a message for 5 seconds...")
    timeout = time.time() + 5
    while time.time() < timeout:
        msg = bus.recv(timeout=1.0)
        if msg:
            print(f"📥 Received: ID=0x{msg.arbitration_id:X}, Data={list(msg.data)}")
            break
    else:
        print("⏰ No message received in 5 seconds.")

if __name__ == "__main__":
    main()
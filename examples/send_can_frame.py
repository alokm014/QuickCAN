# Example: Send a CAN frame
from quickcan.driver import QuickCAN

def on_receive(frame):
    print("Received CAN frame:", frame)

can = QuickCAN(port="COM5")  # Change to your port
can.set_receive_callback(on_receive)

can.send(0x123, [0x11, 0x22, 0x33, 0x44])
print("Frame sent.")

import time
time.sleep(2)

can.close()

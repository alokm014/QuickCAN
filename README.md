# QuickCAN Project

Fast USB to CAN library with python-can support.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

# QuickCAN

**QuickCAN** is a lightweight and scalable USB-to-CAN interface implementation written in Python. It provides a simple serial protocol to send and receive CAN frames, built for rapid development and embedded hardware integration.

---

## 🚀 Features

- ✅ Simple and reliable serial protocol
- ✅ CAN frame support (standard and extended)
- ✅ Escape byte handling
- ✅ Frame streaming and reassembly
- ✅ Command-based messaging (ACK, NACK, HEARTBEAT, CONFIG, etc.)
- ✅ Python CAN interface compatible (`python-can` backend support)
- ✅ CLI tools to send and receive CAN data
- ✅ Arduino-compatible testing firmware
- ✅ Unit tested and extensible

---

## ⚙️ Installation

```bash
git clone https://github.com/yourname/QuickCAN.git
cd QuickCAN
pip install -e .
```

Or install using requirements:

```bash
pip install -r requirements.txt
```

---

## 🔧 Usage

### CLI Example

```bash
# Send CAN frame (ID=0x123, data=[0x01, 0x02])
quickcan-cli --port COM5 --send 0x123 0x01 0x02

# Receive CAN frames
quickcan-cli --port COM5 --recv
```

### Python API Example

```python
from quickcan.driver import QuickCAN

def on_receive(cmd, frame):
    print(f"CMD={cmd}, ID=0x{frame.can_id:X}, DATA={frame.data}")

can = QuickCAN("COM5")
can.set_receive_callback(on_receive)
can.send(0x123, [0x01, 0x02])
```

---

## 🔌 Arduino Testing

Use the provided Arduino sketch to send various protocol commands for testing the QuickCAN Python interface.

---

## 📦 Supported Commands

| Command       | Code  | Description              |
|---------------|-------|--------------------------|
| CAN_SEND      | 0x01  | Send CAN frame           |
| HEARTBEAT     | 0x02  | Periodic heartbeat       |
| ACK           | 0x03  | Acknowledge frame        |
| NACK          | 0x04  | Negative Acknowledge     |
| DEVICE_INFO   | 0x10  | Get device info          |
| PING          | 0x20  | Ping                     |
| CONFIG_GET    | 0x30  | Request config value     |
| CONFIG_SET    | 0x31  | Set config value         |
| RESET         | 0x40  | Reset device             |
| SET_FILTER    | 0x41  | Set CAN filter           |
| CLEAR_FILTER  | 0x42  | Clear CAN filter         |

---

## 🧪 Testing

Run all unit tests using:

```bash
pytest tests/
```

---

## 📜 License

MIT License - feel free to use and modify.

---

## 🙌 Contributors

- **Alok Mishra** — Initial design, protocol, CLI & implementation
- You? PRs welcome! 🎉

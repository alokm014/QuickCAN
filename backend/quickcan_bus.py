# python-can backend interface class for QuickCAN
import can
import threading
import queue
from quickcan.driver import QuickCAN

class QuickCANBus(can.BusABC):
    def __init__(self, channel, bitrate=500000, *args, **kwargs):
        self._interface = QuickCAN(channel)
        self._recv_queue = queue.Queue()
        self._shutdown = threading.Event()

        self._interface.set_receive_callback(self._on_frame_received)

        self._recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._recv_thread.start()

    def send(self, msg: can.Message, timeout=None):
        data = list(msg.data)
        self._interface.send(msg.arbitration_id, data, extended=msg.is_extended_id)

    def _on_frame_received(self, frame):
        msg = can.Message(
            arbitration_id=frame.can_id,
            data=frame.data,
            is_extended_id=frame.extended
        )
        self._recv_queue.put(msg)

    def _receive_loop(self):
        while not self._shutdown.is_set():
            try:
                self._interface.receive()
            except Exception:
                continue

    def recv(self, timeout=None) -> can.Message:
        try:
            return self._recv_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def shutdown(self):
        self._shutdown.set()
        self._recv_thread.join()
        self._interface.close()

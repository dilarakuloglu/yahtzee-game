import socket
import json
import threading
from PyQt6.QtCore import QObject, pyqtSignal


class NetworkClient(QObject):
    # Sinyaller
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    message_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sock = None
        self.running = False
        self._thread = None

    def connect_to_server(self, host, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((host, int(port)))
            self.sock.settimeout(None)
            self.running = True
            self._thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._thread.start()
            self.connected.emit()
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False

    def send(self, message: dict):
        if self.sock and self.running:
            try:
                data = json.dumps(message) + "\n"
                self.sock.sendall(data.encode())
            except Exception as e:
                self.error_occurred.emit(str(e))

    def _receive_loop(self):
        buffer = ""
        try:
            while self.running:
                chunk = self.sock.recv(4096).decode()
                if not chunk:
                    break
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        try:
                            msg = json.loads(line)
                            self.message_received.emit(msg)
                        except json.JSONDecodeError:
                            pass
        except Exception:
            pass
        finally:
            self.running = False
            self.disconnected.emit()

    def disconnect(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

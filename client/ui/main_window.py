"""
Ana pencere - ekran geçişlerini yönetir
"""

from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from ui.screens.start_screen import StartScreen
from ui.screens.lobby_screen import LobbyScreen
from ui.screens.game_screen import GameScreen
from ui.screens.end_screen import EndScreen
from ui.network_client import NetworkClient


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yahtzee")
        self.setMinimumSize(QSize(900, 700))
        self.resize(1000, 750)

        self.network = NetworkClient()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Ekranlar
        self.start_screen = StartScreen(self)
        self.lobby_screen = LobbyScreen(self)
        self.game_screen = GameScreen(self)
        self.end_screen = EndScreen(self)

        self.stack.addWidget(self.start_screen)   # 0
        self.stack.addWidget(self.lobby_screen)   # 1
        self.stack.addWidget(self.game_screen)    # 2
        self.stack.addWidget(self.end_screen)     # 3

        # Ağ sinyalleri
        self.network.connected.connect(self._on_connected)
        self.network.disconnected.connect(self._on_disconnected)
        self.network.message_received.connect(self._on_message)
        self.network.error_occurred.connect(self._on_error)

        self.player_name = ""
        self.show_start()

    def show_start(self):
        self.stack.setCurrentIndex(0)

    def show_lobby(self):
        self.stack.setCurrentIndex(1)

    def show_game(self):
        self.stack.setCurrentIndex(2)

    def show_end(self):
        self.stack.setCurrentIndex(3)

    def connect_to_server(self, host, port, name):
        self.player_name = name
        self.network.connect_to_server(host, port)

    def _on_connected(self):
        self.network.send({"type": "join", "name": self.player_name})

    def _on_disconnected(self):
        self.start_screen.show_error("Sunucu bağlantısı kesildi.")
        self.show_start()

    def _on_error(self, err):
        self.start_screen.show_error(f"Bağlantı hatası: {err}")

    def _on_message(self, msg):
        mtype = msg.get("type")

        if mtype in ("joined", "waiting"):
            self.lobby_screen.update_state(msg)
            self.show_lobby()

        elif mtype == "game_start":
            self.game_screen.init_game(msg, self.player_name, self.network)
            self.show_game()

        elif mtype in ("turn_state", "score_update", "restart_vote"):
            self.game_screen.handle_message(msg)

        elif mtype == "game_over":
            self.end_screen.show_results(msg, self.player_name, self.network)
            self.show_end()

        elif mtype == "player_left":
            self.game_screen.show_notification(msg.get("msg", "Oyuncu ayrıldı."))

    def closeEvent(self, event):
        self.network.disconnect()
        event.accept()

import os
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6 import uic
from PyQt6.QtGui import QFont


class LobbyScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        uic.loadUi(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "lobby_screen.ui"),
            self
        )
        self.backBtn.clicked.connect(self._on_back)

    def _on_back(self):
        self.main_window._leaving_intentionally = True
        self.main_window.network.disconnect()
        self.main_window.show_start()

    def update_state(self, msg):
        mtype = msg.get("type")
        players = msg.get("players", [])

        while self.playersLayout.count():
            item = self.playersLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for p in players:
            lbl = QLabel(f"- {p}")
            lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            lbl.setStyleSheet("background: transparent; color: #212121;")
            self.playersLayout.addWidget(lbl)

        if mtype in ("joined", "waiting"):
            needed = 2 - len(players)
            if needed > 0:
                self.statusLabel.setText(f"{needed} oyuncu daha bekleniyor")

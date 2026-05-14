"""
Bekleme Odasi Ekrani
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class LobbyScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #EEF2FF;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedWidth(440)
        card.setStyleSheet("background: white; border-radius: 20px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 40))
        card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(card)
        cl.setSpacing(16)
        cl.setContentsMargins(40, 36, 40, 36)

        title_lbl = QLabel("Bekleme Odasi")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #1976D2;")
        cl.addWidget(title_lbl)

        self.status_lbl = QLabel("Diger oyuncu bekleniyor")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #757575; font-size: 14px;")
        cl.addWidget(self.status_lbl)

        self.players_frame = QFrame()
        self.players_frame.setStyleSheet("background: #F8F9FA; border-radius: 10px;")
        self.players_layout = QVBoxLayout(self.players_frame)
        self.players_layout.setContentsMargins(16, 12, 16, 12)
        self.players_layout.setSpacing(8)
        cl.addWidget(self.players_frame)

        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_state(self, msg):
        mtype = msg.get("type")
        players = msg.get("players", [])

        while self.players_layout.count():
            item = self.players_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for p in players:
            lbl = QLabel(f"- {p}")
            lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            lbl.setStyleSheet("background: transparent; color: #212121;")
            self.players_layout.addWidget(lbl)

        if mtype in ("joined", "waiting"):
            needed = 2 - len(players)
            if needed > 0:
                self.status_lbl.setText(f"{needed} oyuncu daha bekleniyor")

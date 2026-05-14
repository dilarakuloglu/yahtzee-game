import os
from PyQt6.QtWidgets import QWidget, QFrame, QHBoxLayout, QLabel
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from logic.game_logic import CATEGORIES, CATEGORY_NAMES, UPPER_CATEGORIES
from ..network_client import NetworkClient


class EndScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.network = None
        uic.loadUi(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "end_screen.ui"),
            self
        )
        self.restartBtn.clicked.connect(self._on_restart)
        self.menuBtn.clicked.connect(self._on_menu)

    def show_results(self, msg, player_name, network):
        self.network = network
        self.player_name = player_name
        winner = msg.get("winner", "")
        totals = msg.get("totals", {})
        scores = msg.get("scores", {})
        players = list(scores.keys())

        if winner == player_name:
            self.winnerLabel.setText("Tebrikler, kazandınız!")
            self.winnerLabel.setStyleSheet("color: #00A651; font-size: 24px; font-weight: bold;")
        else:
            self.winnerLabel.setText(f"{winner} kazandı!")
            self.winnerLabel.setStyleSheet("color: #F57F17; font-size: 24px; font-weight: bold;")
        self.winnerScoreLabel.setText(f"Kazanan skoru: {totals.get(winner, 0)} puan")

        while self.scoreInnerLayout.count():
            item = self.scoreInnerLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        header = QFrame()
        header.setStyleSheet("background: #00A651;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(8, 4, 8, 4)
        cat_h = QLabel("Kategori")
        cat_h.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        cat_h.setStyleSheet("color: white; background: transparent;")
        hl.addWidget(cat_h, 2)
        for p in players:
            pl = QLabel(p)
            pl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            pl.setStyleSheet("color: white; background: transparent;")
            pl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hl.addWidget(pl, 1)
        self.scoreInnerLayout.addWidget(header)

        for idx, cat in enumerate(CATEGORIES):
            row = QFrame()
            row.setStyleSheet(f"background: {'#F5F5F5' if idx % 2 == 0 else 'white'};")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(8, 2, 8, 2)
            name_lbl = QLabel(CATEGORY_NAMES[cat])
            name_lbl.setStyleSheet("background: transparent; font-size: 12px;")
            rl.addWidget(name_lbl, 2)
            for p in players:
                val = scores.get(p, {}).get(cat, "—")
                vl = QLabel(str(val))
                vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                vl.setStyleSheet("background: transparent;")
                rl.addWidget(vl, 1)
            self.scoreInnerLayout.addWidget(row)

        bonus_row = QFrame()
        bonus_row.setStyleSheet("background: #FFF8E1;")
        bl = QHBoxLayout(bonus_row)
        bl.setContentsMargins(8, 2, 8, 2)
        bl.addWidget(QLabel("Bonus (+35)"), 2)
        for p in players:
            upper = sum(scores.get(p, {}).get(c, 0) for c in UPPER_CATEGORIES)
            bonus = 35 if upper >= 63 else 0
            bv = QLabel(str(bonus) if bonus else "—")
            bv.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bl.addWidget(bv, 1)
        self.scoreInnerLayout.addWidget(bonus_row)

        total_row = QFrame()
        total_row.setStyleSheet("background: #00A651;")
        tl = QHBoxLayout(total_row)
        tl.setContentsMargins(8, 4, 8, 4)
        total_name = QLabel("TOPLAM")
        total_name.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        total_name.setStyleSheet("background: transparent; color: white;")
        tl.addWidget(total_name, 2)
        for p in players:
            tv = QLabel(str(totals.get(p, 0)))
            tv.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tv.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            tv.setStyleSheet("background: transparent; color: white;")
            tl.addWidget(tv, 1)
        self.scoreInnerLayout.addWidget(total_row)
        self.scoreInnerLayout.addStretch()

        self.statusLabel.setText("")
        self.restartBtn.setEnabled(True)
        self.restartBtn.setText("Yeniden Oyna")

    def _on_restart(self):
        if self.network:
            self.network.send({"type": "restart"})
            self.restartBtn.setText("Bekleniyor...")
            self.restartBtn.setEnabled(False)
            self.statusLabel.setText("Diğer oyuncunun onayı bekleniyor...")

    def _on_menu(self):
        if self.network:
            self.network.disconnect()
        self.main_window.network = NetworkClient()
        mw = self.main_window
        mw.network.connected.connect(mw._on_connected)
        mw.network.disconnected.connect(mw._on_disconnected)
        mw.network.message_received.connect(mw._on_message)
        mw.network.error_occurred.connect(mw._on_error)
        mw.start_screen._reset_button()
        mw.start_screen.errorLabel.setText("")
        mw.show_start()

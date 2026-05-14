"""
Bitis Ekrani
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from logic.game_logic import CATEGORIES, CATEGORY_NAMES, UPPER_CATEGORIES
from ..network_client import NetworkClient


class EndScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.network = None
        self._build_ui()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)

        winner_group = QGroupBox("Sonuc")
        winner_group.setFont(QFont("Segoe UI", 10))
        wl = QVBoxLayout(winner_group)
        wl.setSpacing(6)

        self.winner_lbl = QLabel("")
        self.winner_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winner_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        wl.addWidget(self.winner_lbl)

        self.winner_score_lbl = QLabel("")
        self.winner_score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wl.addWidget(self.winner_score_lbl)

        self.main_layout.addWidget(winner_group)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(340)

        self.score_container = QWidget()
        self.score_inner = QVBoxLayout(self.score_container)
        self.score_inner.setSpacing(2)
        self.score_inner.setContentsMargins(0, 0, 4, 0)

        scroll.setWidget(self.score_container)
        self.main_layout.addWidget(scroll, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.restart_btn = QPushButton("Yeniden Oyna")
        self.restart_btn.setFixedHeight(36)
        self.restart_btn.clicked.connect(self._on_restart)
        btn_row.addWidget(self.restart_btn)

        self.menu_btn = QPushButton("Ana Menu")
        self.menu_btn.setFixedHeight(36)
        self.menu_btn.clicked.connect(self._on_menu)
        btn_row.addWidget(self.menu_btn)

        self.main_layout.addLayout(btn_row)

        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_lbl)

    def show_results(self, msg, player_name, network):
        self.network = network
        self.player_name = player_name
        winner = msg.get("winner", "")
        totals = msg.get("totals", {})
        scores = msg.get("scores", {})
        players = list(scores.keys())

        if winner == player_name:
            self.winner_lbl.setText("Tebrikler, kazandiniz!")
            self.winner_lbl.setStyleSheet("color: green;")
        else:
            self.winner_lbl.setText(f"{winner} kazandi!")
            self.winner_lbl.setStyleSheet("")
        self.winner_score_lbl.setText(f"Kazanan skoru: {totals.get(winner, 0)} puan")

        while self.score_inner.count():
            item = self.score_inner.takeAt(0)
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
        self.score_inner.addWidget(header)

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
            self.score_inner.addWidget(row)

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
        self.score_inner.addWidget(bonus_row)

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
        self.score_inner.addWidget(total_row)
        self.score_inner.addStretch()

        self.status_lbl.setText("")
        self.restart_btn.setEnabled(True)
        self.restart_btn.setText("Yeniden Oyna")

    def _on_restart(self):
        if self.network:
            self.network.send({"type": "restart"})
            self.restart_btn.setText("Bekleniyor...")
            self.restart_btn.setEnabled(False)
            self.status_lbl.setText("Diger oyuncunun onayi bekleniyor...")

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
        mw.start_screen.error_label.setText("")
        mw.show_start()

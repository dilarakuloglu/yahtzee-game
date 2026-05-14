"""
Baslangic Ekrani
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush


class DiceWidget(QLabel):
    DOTS = {
        1: [(0.5, 0.5)],
        2: [(0.25, 0.25), (0.75, 0.75)],
        3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
        4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
        5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
        6: [(0.25, 0.2), (0.75, 0.2), (0.25, 0.5), (0.75, 0.5), (0.25, 0.8), (0.75, 0.8)],
    }

    def __init__(self, value=1, size=48, color="#00A651"):
        super().__init__()
        self.value = value
        self.dice_size = size
        self.color = color
        self.setFixedSize(size, size)

    def set_value(self, v):
        self.value = v
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(self.color)))
        p.setPen(Qt.PenStyle.NoPen)
        r = self.dice_size * 0.18
        p.drawRoundedRect(2, 2, self.dice_size - 4, self.dice_size - 4, r, r)
        p.setBrush(QBrush(QColor("white")))
        dot_r = self.dice_size * 0.1
        for (fx, fy) in self.DOTS.get(self.value, []):
            cx = fx * (self.dice_size - 4) + 2
            cy = fy * (self.dice_size - 4) + 2
            p.drawEllipse(int(cx - dot_r), int(cy - dot_r), int(dot_r * 2), int(dot_r * 2))


class StartScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()
        self._start_animations()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("YAHTZEE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        layout.addWidget(title)

        dice_row = QHBoxLayout()
        dice_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dice_row.setSpacing(8)
        self.dice_widgets = []
        colors = ["#00A651", "#E53935", "#43A047", "#FB8C00", "#8E24AA"]
        for i, c in enumerate(colors):
            d = DiceWidget(i + 1, 48, c)
            dice_row.addWidget(d)
            self.dice_widgets.append(d)
        layout.addLayout(dice_row)

        group = QGroupBox("Baglanti")
        group.setFixedWidth(380)
        group.setFont(QFont("Segoe UI", 10))
        form = QVBoxLayout(group)
        form.setSpacing(8)

        form.addWidget(QLabel("Oyuncu Adi"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Adinizi girin...")
        self.name_input.setMaxLength(20)
        form.addWidget(self.name_input)

        form.addWidget(QLabel("Sunucu IP Adresi"))
        ip_row = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("13.53.91.129")
        self.ip_input.setText("13.53.91.129")
        ip_row.addWidget(self.ip_input, 3)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")
        self.port_input.setText("8080")
        self.port_input.setMaximumWidth(80)
        ip_row.addWidget(self.port_input, 1)
        form.addLayout(ip_row)

        self.connect_btn = QPushButton("Baglан")
        self.connect_btn.setFixedHeight(36)
        self.connect_btn.clicked.connect(self._on_connect)
        form.addWidget(self.connect_btn)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)
        form.addWidget(self.error_label)

        layout.addWidget(group, alignment=Qt.AlignmentFlag.AlignCenter)

        self.name_input.returnPressed.connect(self._on_connect)
        self.port_input.returnPressed.connect(self._on_connect)

    def _start_animations(self):
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate_dice)
        self._anim_timer.start(800)

    def _animate_dice(self):
        import random
        for d in self.dice_widgets:
            d.set_value(random.randint(1, 6))

    def _on_connect(self):
        name = self.name_input.text().strip()
        ip = self.ip_input.text().strip()
        port = self.port_input.text().strip()

        if not name:
            self.show_error("Lutfen adinizi girin.")
            return
        if not ip:
            self.show_error("Lutfen sunucu IP adresini girin.")
            return
        if not port.isdigit():
            self.show_error("Gecerli bir port numarasi girin.")
            return

        self.error_label.setText("")
        self.connect_btn.setText("Baglaniliyor...")
        self.connect_btn.setEnabled(False)
        self.main_window.connect_to_server(ip, port, name)

        QTimer.singleShot(11000, self._reset_button)

    def _reset_button(self):
        self.connect_btn.setText("Baglan")
        self.connect_btn.setEnabled(True)

    def show_error(self, msg):
        self._reset_button()
        self.error_label.setText(msg)

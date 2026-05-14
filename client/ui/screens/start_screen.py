import os
import random
from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush
from PyQt6.QtWidgets import QLabel


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
        uic.loadUi(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "start_screen.ui"),
            self
        )
        self._setup_dice()
        self._setup_connections()
        self._start_animations()

    def _setup_dice(self):
        colors = ["#00A651", "#E53935", "#43A047", "#FB8C00", "#8E24AA"]
        self.dice_widgets = []
        layout = self.diceRow.layout()
        for i, c in enumerate(colors):
            d = DiceWidget(i + 1, 48, c)
            layout.addWidget(d)
            self.dice_widgets.append(d)

    def _setup_connections(self):
        self.ipInput.setText("13.53.91.129")
        self.portInput.setText("8080")
        self.connectBtn.clicked.connect(self._on_connect)
        self.nameInput.returnPressed.connect(self._on_connect)
        self.portInput.returnPressed.connect(self._on_connect)

    def _start_animations(self):
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate_dice)
        self._anim_timer.start(800)

    def _animate_dice(self):
        for d in self.dice_widgets:
            d.set_value(random.randint(1, 6))

    def _on_connect(self):
        name = self.nameInput.text().strip()
        ip = self.ipInput.text().strip()
        port = self.portInput.text().strip()

        if not name:
            self.show_error("Lutfen adinizi girin.")
            return
        if not ip:
            self.show_error("Lutfen sunucu IP adresini girin.")
            return
        if not port.isdigit():
            self.show_error("Gecerli bir port numarasi girin.")
            return

        self.errorLabel.setText("")
        self.connectBtn.setText("Baglaniliyor...")
        self.connectBtn.setEnabled(False)
        self.main_window.connect_to_server(ip, port, name)
        QTimer.singleShot(11000, self._reset_button)

    def _reset_button(self):
        self.connectBtn.setText("Baglan")
        self.connectBtn.setEnabled(True)

    def show_error(self, msg):
        self._reset_button()
        self.errorLabel.setText(msg)

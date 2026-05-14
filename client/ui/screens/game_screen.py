import os
from PyQt6.QtWidgets import QWidget, QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen

from logic.game_logic import CATEGORIES, CATEGORY_NAMES, UPPER_CATEGORIES, LOWER_CATEGORIES, calculate_score

DOTS = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
    6: [(0.25, 0.18), (0.75, 0.18), (0.25, 0.5), (0.75, 0.5), (0.25, 0.82), (0.75, 0.82)],
}


class AnimatedDie(QWidget):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.value = 1
        self.kept = False
        self.rolling = False
        self.enabled_die = True
        self._anim_value = 1
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._roll_frame)
        self._anim_steps = 0
        self.setFixedSize(80, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._callback = None

    def set_callback(self, cb):
        self._callback = cb

    def set_state(self, value, kept, enabled):
        self.value = value
        self.kept = kept
        self.enabled_die = enabled
        self.update()

    def animate_roll(self, final_value, done_cb=None):
        if self.kept:
            return
        self.rolling = True
        self._final_value = final_value
        self._anim_steps = 10
        self._done_cb = done_cb
        self._anim_timer.start(40)

    def _roll_frame(self):
        import random
        self._anim_steps -= 1
        self._anim_value = random.randint(1, 6)
        self.update()
        if self._anim_steps <= 0:
            self._anim_timer.stop()
            self.rolling = False
            self.value = self._final_value
            self._anim_value = self._final_value
            self.update()
            if self._done_cb:
                self._done_cb()

    def mousePressEvent(self, event):
        if self.enabled_die and not self.rolling and self._callback:
            self._callback(self.index)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()
        margin = 4

        if self.kept:
            bg = QColor("#FFF9C4")
            border = QColor("#F9A825")
        elif not self.enabled_die:
            bg = QColor("#F5F5F5")
            border = QColor("#E0E0E0")
        else:
            bg = QColor("white")
            border = QColor("#80D4A8")

        p.setPen(QPen(border, 2.5))
        p.setBrush(QBrush(bg))
        p.drawRoundedRect(margin, margin, W - margin*2, H - margin*2, 12, 12)

        val = self._anim_value if self.rolling else self.value

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#E53935") if not self.kept else QColor("#E65100")))

        dot_r = 6
        inner_w = W - margin*2 - 16
        inner_h = H - margin*2 - 16
        ox = margin + 8
        oy = margin + 8

        for (fx, fy) in DOTS.get(val, []):
            cx = int(ox + fx * inner_w)
            cy = int(oy + fy * inner_h)
            p.drawEllipse(cx - dot_r, cy - dot_r, dot_r*2, dot_r*2)

        if self.kept:
            p.setPen(QPen(QColor("#F9A825"), 2))
            p.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
            p.drawText(0, H - 4, W, 12, Qt.AlignmentFlag.AlignCenter, "TUTULDU")


class GameScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.network = None
        self.player_name = ""
        self.my_turn = False
        self.scores = {}
        self.players = []
        self.current_player = ""
        self.dice = [1]*5
        self.kept = [False]*5
        self.rolls_left = 3

        uic.loadUi(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_files", "game_screen.ui"),
            self
        )
        self._setup_dice()
        self.rollBtn.clicked.connect(self._on_roll)

    def _setup_dice(self):
        self.dice_widgets = []
        layout = self.diceRow.layout()
        for i in range(5):
            d = AnimatedDie(i)
            d.set_callback(self._toggle_keep)
            layout.addWidget(d)
            self.dice_widgets.append(d)

    def init_game(self, msg, player_name, network):
        self.player_name = player_name
        self.network = network
        self.players = msg.get("players", [])
        self.scores = {p: {} for p in self.players}
        self.current_player = msg.get("current_player", "")
        self._build_score_card()

    def _build_score_card(self):
        while self.scoreLayout.count():
            item = self.scoreLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.score_rows = {}

        header = QFrame()
        header.setStyleSheet("background: #00A651; border-radius: 10px;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 8, 12, 8)
        cat_h = QLabel("Kategori")
        cat_h.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cat_h.setStyleSheet("color: white; background: transparent;")
        hl.addWidget(cat_h, 2)

        for p in self.players:
            short = p[:10] + ("..." if len(p) > 10 else "")
            pl = QLabel(short)
            pl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            pl.setStyleSheet("color: white; background: transparent;")
            pl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hl.addWidget(pl, 1)

        self.scoreLayout.addWidget(header)

        upper_lbl = QLabel("  UST BOLUM")
        upper_lbl.setStyleSheet("color: #757575; font-size: 10px; font-weight: bold; background:transparent;")
        self.scoreLayout.addWidget(upper_lbl)

        for i, cat in enumerate(UPPER_CATEGORIES):
            self.scoreLayout.addWidget(self._make_score_row(cat, i))

        self.scoreLayout.addWidget(self._make_bonus_row())

        lower_lbl = QLabel("  ALT BOLUM")
        lower_lbl.setStyleSheet("color: #757575; font-size: 10px; font-weight: bold; background:transparent;")
        self.scoreLayout.addWidget(lower_lbl)

        for i, cat in enumerate(LOWER_CATEGORIES):
            self.scoreLayout.addWidget(self._make_score_row(cat, i + 6))

        self.scoreLayout.addWidget(self._make_total_row())
        self.scoreLayout.addStretch()

    def _make_score_row(self, cat, idx):
        row = QFrame()
        row.setStyleSheet(f"background: {'#FAFAFA' if idx % 2 == 0 else 'white'}; border-radius: 6px;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 6, 12, 6)
        rl.setSpacing(0)

        name_lbl = QLabel(CATEGORY_NAMES[cat])
        name_lbl.setStyleSheet("color: #424242; background: transparent; font-size: 12px;")
        rl.addWidget(name_lbl, 2)

        score_btns = {}
        for p in self.players:
            btn = QPushButton("—")
            btn.setFixedHeight(36)
            btn.setMinimumWidth(70)
            btn.setFont(QFont("Segoe UI", 12))
            btn.setStyleSheet("""
                QPushButton { background: transparent; color: #9E9E9E; border: none; }
                QPushButton:hover { background: #E8F5E9; border-radius: 6px; color: #00A651; }
                QPushButton:disabled { color: #9E9E9E; background: transparent; }
            """)
            btn.setProperty("category", cat)
            btn.setProperty("player", p)
            btn.clicked.connect(lambda checked=False, c=cat: self._on_score_select(c))
            btn.setEnabled(False)
            rl.addWidget(btn, 1)
            score_btns[p] = btn

        self.score_rows[cat] = score_btns
        return row

    def _make_bonus_row(self):
        row = QFrame()
        row.setStyleSheet("background: #FFF8E1; border-radius: 6px;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 6, 12, 6)

        name_lbl = QLabel("Bonus (63 puan -> +35)")
        name_lbl.setStyleSheet("color: #E65100; font-size: 11px; font-weight: bold; background: transparent;")
        rl.addWidget(name_lbl, 2)

        self.bonus_labels = {}
        for p in self.players:
            lbl = QLabel("—")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #E65100; font-weight: bold; background: transparent;")
            rl.addWidget(lbl, 1)
            self.bonus_labels[p] = lbl

        return row

    def _make_total_row(self):
        row = QFrame()
        row.setStyleSheet("background: #00A651; border-radius: 8px; margin-top: 4px;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 8, 12, 8)

        lbl = QLabel("TOPLAM")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl.setStyleSheet("color: white; background: transparent;")
        rl.addWidget(lbl, 2)

        self.total_labels = {}
        for p in self.players:
            tl = QLabel("0")
            tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            tl.setStyleSheet("color: white; background: transparent;")
            rl.addWidget(tl, 1)
            self.total_labels[p] = tl

        return row

    def handle_message(self, msg):
        mtype = msg.get("type")
        if mtype == "turn_state":
            self._apply_turn_state(msg)
        elif mtype == "score_update":
            self.scores = msg.get("scores", self.scores)
            self._update_score_display()
        elif mtype == "restart_vote":
            voter = msg.get("voter", "")
            count = msg.get("count", 0)
            needed = msg.get("needed", 2)
            self.show_notification(f"{voter} yeniden oynamak istiyor. ({count}/{needed})")

    def _apply_turn_state(self, msg):
        self.current_player = msg.get("current_player", "")
        self.dice = msg.get("dice", [1]*5)
        self.kept = msg.get("kept", [False]*5)
        self.rolls_left = msg.get("rolls_left", 3)
        self.my_turn = msg.get("your_turn", False)
        self.scores = msg.get("scores", self.scores)

        if self.my_turn:
            self.turnLabel.setText("Sira Sizde!")
            self.turnLabel.setStyleSheet(
                "background: white; border-radius: 12px; padding: 12px; color: #2E7D32; font-size: 15px; font-weight: bold;"
            )
        else:
            self.turnLabel.setText(f"{self.current_player}'in sirasi")
            self.turnLabel.setStyleSheet(
                "background: white; border-radius: 12px; padding: 12px; color: #00A651; font-size: 15px; font-weight: bold;"
            )

        self.rollsLabel.setText(f"Atis hakki: {self.rolls_left}")
        self._animate_dice_roll()
        self.rollBtn.setEnabled(self.my_turn and self.rolls_left > 0)
        self._update_score_buttons()
        self._update_score_display()

    def _animate_dice_roll(self):
        pending = [0]
        total = sum(1 for k in self.kept if not k)
        if total == 0:
            for i, d in enumerate(self.dice_widgets):
                d.set_state(self.dice[i], self.kept[i], self.my_turn)
            return

        def one_done():
            pending[0] += 1

        for i, d in enumerate(self.dice_widgets):
            if not self.kept[i]:
                d.kept = False
                d.enabled_die = self.my_turn
                d.animate_roll(self.dice[i], one_done)
            else:
                d.set_state(self.dice[i], self.kept[i], self.my_turn)

    def _toggle_keep(self, idx):
        if not self.my_turn or self.rolls_left >= 3:
            return
        self.kept[idx] = not self.kept[idx]
        self.dice_widgets[idx].kept = self.kept[idx]
        self.dice_widgets[idx].update()
        self.rollBtn.setEnabled(self.rolls_left > 0 and not all(self.kept))

    def _on_roll(self):
        if not self.my_turn or self.rolls_left <= 0:
            return
        kept_indices = [i for i, k in enumerate(self.kept) if k]
        self.rollBtn.setEnabled(False)
        self.network.send({"type": "roll", "kept": kept_indices})

    def _update_score_buttons(self):
        for cat, player_btns in self.score_rows.items():
            for p, btn in player_btns.items():
                if p == self.player_name and self.my_turn and self.rolls_left < 3:
                    if cat not in self.scores.get(p, {}):
                        preview = calculate_score(cat, self.dice)
                        btn.setText(f"+{preview}" if preview > 0 else "0")
                        btn.setEnabled(True)
                        btn.setStyleSheet("""
                            QPushButton { background: #E8F5E9; color: #00A651;
                                border: 1px solid #80D4A8; border-radius: 6px; font-weight: bold; }
                            QPushButton:hover { background: #C8E6C9; }
                        """)
                    else:
                        score = self.scores.get(p, {}).get(cat, "—")
                        btn.setText(str(score))
                        btn.setEnabled(False)
                        btn.setStyleSheet("QPushButton { background: transparent; color: #424242; border: none; font-weight: bold; }")
                else:
                    score = self.scores.get(p, {}).get(cat)
                    btn.setText(str(score) if score is not None else "—")
                    btn.setEnabled(False)
                    color = "#424242" if score is not None else "#BDBDBD"
                    btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {color}; border: none; }}")

    def _on_score_select(self, category):
        self.network.send({"type": "score", "category": category})

    def _update_score_display(self):
        for p in self.players:
            p_scores = self.scores.get(p, {})
            for cat, btns in self.score_rows.items():
                if cat in p_scores and p in btns:
                    btn = btns[p]
                    if p != self.player_name or not self.my_turn or cat in p_scores:
                        btn.setText(str(p_scores[cat]))
                        btn.setEnabled(False)

            upper = sum(p_scores.get(c, 0) for c in UPPER_CATEGORIES)
            filled_upper = sum(1 for c in UPPER_CATEGORIES if c in p_scores)
            if p in self.bonus_labels:
                if filled_upper == len(UPPER_CATEGORIES):
                    bonus = 35 if upper >= 63 else 0
                    self.bonus_labels[p].setText(str(bonus))
                else:
                    self.bonus_labels[p].setText(f"{upper}/63")

            upper_total = sum(p_scores.get(c, 0) for c in UPPER_CATEGORIES)
            bonus = 35 if upper_total >= 63 and filled_upper == len(UPPER_CATEGORIES) else 0
            lower_total = sum(p_scores.get(c, 0) for c in LOWER_CATEGORIES)
            if p in self.total_labels:
                self.total_labels[p].setText(str(upper_total + bonus + lower_total))

    def show_notification(self, msg):
        self.notifLabel.setText(msg)
        self.notifLabel.show()
        QTimer.singleShot(4000, self.notifLabel.hide)

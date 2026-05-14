import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Yahtzee")
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            background-color: #F5F5F5;
            color: #212121;
        }
        QPushButton {
            background-color: #00A651;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #008C44;
        }
        QPushButton:pressed {
            background-color: #006B33;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
            color: #757575;
        }
        QLineEdit {
            border: 2px solid #BDBDBD;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: white;
            font-size: 14px;
        }
        QLineEdit:focus {
            border-color: #00A651;
        }
        QLabel {
            background: transparent;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        QScrollBar:vertical {
            width: 8px;
            background: #EEEEEE;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #BDBDBD;
            border-radius: 4px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

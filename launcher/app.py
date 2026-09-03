"""Entry point for the Pixel Launcher."""
import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication

from .core.paths import tile
from .ui.main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("Pixel Launcher")
    app.setWindowIcon(QIcon(tile("torii")))
    app.setFont(QFont("Noto Sans", 9))

    window = MainWindow()
    window.show()
    QTimer.singleShot(150, window.prompt_login)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""Server rows, shown in the flyout behind the status bar's server chip."""
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QWidget

from ...core import theme

STATUS_COLORS = {"online": theme.MOSS, "busy": theme.ORANGE, "offline": theme.ROSE}


class ServerRow(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent)
        self.server = server
        self.setFixedHeight(26)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        color = QColor(STATUS_COLORS.get(self.server["status"], theme.TEXT_FAINT))

        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawEllipse(QRectF(2, self.height() / 2 - 3, 6, 6))

        p.setFont(QFont("Noto Sans", 9))
        p.setPen(QColor(theme.TEXT_DIM))
        p.drawText(18, int(self.height() / 2 + 4), self.server["name"])

        # Load meter, four blocks, filled to match capacity.
        blocks, x = 4, self.width() - 96
        filled = round(self.server["load"] * blocks)
        for i in range(blocks):
            p.setBrush(color if i < filled else QColor(255, 255, 255, 22))
            p.drawRoundedRect(QRectF(x + i * 9, self.height() / 2 - 4, 6, 8), 1, 1)

        p.setPen(QColor(theme.TEXT_FAINT))
        p.setFont(QFont("Noto Sans", 8))
        label = f"{self.server['ping']} ms" if self.server["status"] != "offline" else "down"
        p.drawText(self.width() - 46, int(self.height() / 2 + 4), label)
        p.end()

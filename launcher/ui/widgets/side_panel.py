"""Right-hand column: server status and the shortcut buttons."""
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame

from qfluentwidgets import (StrongBodyLabel, setFont, FluentIcon, BodyLabel,
                            TransparentToolButton, SingleDirectionScrollArea,
                            ToolTipFilter)

from ...core import pixel, theme
from ...core.paths import tile

STATUS_COLORS = {"online": theme.MOSS, "busy": theme.ORANGE, "offline": theme.ROSE}


class ServerRow(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent)
        self.server = server
        self.setFixedHeight(25)

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


class SidePanel(QWidget):
    shortcut_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(284)
        self.setObjectName("sidePanel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Everything scrolls: the panel has to survive a short window without
        # squeezing its rows on top of each other.
        scroll = SingleDirectionScrollArea(orient=Qt.Vertical)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        holder = QWidget()
        holder.setStyleSheet("background: transparent;")
        scroll.setWidget(holder)
        outer.addWidget(scroll, 1)

        layout = QVBoxLayout(holder)
        layout.setContentsMargins(18, 14, 14, 8)
        layout.setSpacing(10)

        layout.addWidget(self._heading("SPOTLIGHT"))
        self.spotlight = Spotlight()
        layout.addWidget(self.spotlight)

        layout.addSpacing(6)
        layout.addWidget(self._heading("SERVER STATUS"))
        self.server_box = QVBoxLayout()
        self.server_box.setSpacing(0)
        layout.addLayout(self.server_box)
        layout.addStretch(1)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background: {theme.LINE}; border: none;")
        outer.addWidget(divider)

        shortcuts = QHBoxLayout()
        shortcuts.setSpacing(6)
        shortcuts.setContentsMargins(0, 6, 0, 0)
        for icon, tip, key in (
            (FluentIcon.SHOPPING_CART, "Item shop", "shop"),
            (FluentIcon.PEOPLE, "Community", "community"),
            (FluentIcon.CHAT, "Discussion", "community"),
            (FluentIcon.HELP, "Support", "support"),
        ):
            btn = TransparentToolButton(icon)
            btn.setToolTip(tip)
            btn.installEventFilter(ToolTipFilter(btn))
            btn.clicked.connect(lambda checked=False, k=key: self.shortcut_clicked.emit(k))
            shortcuts.addWidget(btn)
        shortcuts.addStretch(1)
        outer.addLayout(shortcuts)
        outer.setContentsMargins(14, 0, 14, 10)

    def _heading(self, text):
        label = StrongBodyLabel(text)
        label.setStyleSheet(f"color: {theme.TEXT_DIM}; letter-spacing: 1.5px;")
        setFont(label, 11, QFont.Bold)
        return label

    def set_servers(self, servers):
        while self.server_box.count():
            item = self.server_box.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for server in servers:
            self.server_box.addWidget(ServerRow(server))

    def set_game(self, game):
        self.spotlight.set_game(game)


class Spotlight(QWidget):
    """Compact card: the selected game's sprite next to its pitch."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(88)
        self._game = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(72, 10, 12, 10)
        self.blurb = BodyLabel("")
        self.blurb.setWordWrap(True)
        self.blurb.setAlignment(Qt.AlignVCenter)
        self.blurb.setStyleSheet(f"color: {theme.TEXT_DIM};")
        setFont(self.blurb, 10)
        layout.addWidget(self.blurb)

    def set_game(self, game):
        self._game = game
        self.blurb.setText(game.blurb)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect())

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(theme.INK))
        p.drawRoundedRect(rect, 10, 10)

        if self._game is None:
            p.end()
            return

        accent = QColor(self._game.accent)
        plate = QRectF(rect.left(), rect.top(), 62, rect.height())
        p.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 38))
        p.drawRoundedRect(plate, 10, 10)
        p.drawRect(QRectF(plate.right() - 10, plate.top(), 10, plate.height()))

        icon = pixel.load(tile(self._game.icon), 1)
        if not icon.isNull():
            scaled = icon.scaled(44, 44, Qt.KeepAspectRatio, Qt.FastTransformation)
            p.drawPixmap(int(plate.center().x() - scaled.width() / 2),
                         int(plate.center().y() - scaled.height() / 2), scaled)
        p.end()

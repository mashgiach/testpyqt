"""Left-hand game selector: pixel icon, title, and live install state."""
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from qfluentwidgets import SingleDirectionScrollArea, CaptionLabel, setFont

from ...core import pixel, theme
from ...core.paths import tile

STATE_TEXT = {
    "ready": "READY",
    "update": "UPDATE",
    "install": "NOT INSTALLED",
    "busy": "DOWNLOADING",
    "running": "RUNNING",
    "maintenance": "MAINTENANCE",
}


class GameRailItem(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.selected = False
        self._hover = 0.0
        self.setFixedHeight(64)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_Hover)

        self._anim = QPropertyAnimation(self, b"hover", self)
        self._anim.setDuration(140)

    def get_hover(self):
        return self._hover

    def set_hover(self, value):
        self._hover = value
        self.update()

    hover = pyqtProperty(float, get_hover, set_hover)

    def enterEvent(self, event):
        self._animate_to(1.0)

    def leaveEvent(self, event):
        self._animate_to(0.0)

    def _animate_to(self, value):
        self._anim.stop()
        self._anim.setStartValue(self._hover)
        self._anim.setEndValue(value)
        self._anim.start()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.game.id)

    def set_selected(self, selected: bool):
        self.selected = selected
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(6, 4, self.width() - 12, self.height() - 8)

        if self.selected:
            p.setBrush(QColor(theme.SURFACE_HI))
        elif self._hover:
            p.setBrush(QColor(255, 255, 255, int(14 * self._hover)))
        else:
            p.setBrush(Qt.NoBrush)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, 8, 8)

        if self.selected:
            p.setBrush(QColor(self.game.accent))
            p.drawRoundedRect(QRectF(r.left(), r.top() + 10, 3, r.height() - 20), 1.5, 1.5)

        icon = pixel.load(tile(self.game.icon), 1)
        if not icon.isNull():
            side = 40
            scaled = icon.scaled(side, side, Qt.KeepAspectRatio, Qt.FastTransformation)
            p.drawPixmap(int(r.left() + 14), int(r.center().y() - scaled.height() / 2), scaled)

        text_x = int(r.left() + 66)
        title_font = QFont("Noto Sans", 10, QFont.DemiBold)
        p.setFont(title_font)
        p.setPen(QColor(theme.TEXT if self.selected or self._hover else theme.TEXT_DIM))
        available = int(r.right() - text_x - 10)
        elided = QFontMetrics(title_font).elidedText(self.game.title, Qt.ElideRight, available)
        p.drawText(text_x, int(r.center().y() - 2), elided)

        p.setFont(QFont("Noto Sans", 7, QFont.Bold))
        p.setPen(QColor(theme.STATE_COLORS.get(self.game.state, theme.TEXT_FAINT)))
        p.drawText(text_x, int(r.center().y() + 15), STATE_TEXT.get(self.game.state, ""))
        p.end()


class GameRail(QWidget):
    """Scrollable stack of GameRailItems."""

    game_selected = pyqtSignal(str)

    def __init__(self, games, parent=None):
        super().__init__(parent)
        self.setFixedWidth(244)
        self.setObjectName("gameRail")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 12)
        layout.setSpacing(8)

        heading = CaptionLabel("MY GAMES")
        heading.setContentsMargins(20, 0, 0, 0)
        heading.setStyleSheet(f"color: {theme.TEXT_FAINT}; letter-spacing: 1px;")
        setFont(heading, 11, QFont.Bold)
        layout.addWidget(heading)

        scroll = SingleDirectionScrollArea(orient=Qt.Vertical)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        holder = QWidget()
        holder.setStyleSheet("background: transparent;")
        inner = QVBoxLayout(holder)
        inner.setContentsMargins(6, 4, 6, 4)
        inner.setSpacing(2)

        self.items = []
        for game in games:
            item = GameRailItem(game)
            item.clicked.connect(self.select)
            inner.addWidget(item)
            self.items.append(item)
        inner.addStretch(1)

        scroll.setWidget(holder)
        layout.addWidget(scroll, 1)


    def select(self, game_id: str):
        for item in self.items:
            item.set_selected(item.game.id == game_id)
        self.game_selected.emit(game_id)

    def refresh(self):
        for item in self.items:
            item.update()

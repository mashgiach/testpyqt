"""Library tab: every game as a card, with a search box."""
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (SearchLineEdit, FlowLayout, SingleDirectionScrollArea,
                            StrongBodyLabel, setFont)

from ..core import pixel, theme
from ..core.paths import tile
from .widgets.game_rail import STATE_TEXT


class GameCard(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setFixedSize(208, 182)
        self.setCursor(Qt.PointingHandCursor)
        self._hover = False

    def enterEvent(self, event):
        self._hover = True
        self.update()

    def leaveEvent(self, event):
        self._hover = False
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.game.id)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0, 0, -1, -1)

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(theme.SURFACE_HI if self._hover else theme.SURFACE))
        p.drawRoundedRect(rect, 12, 12)

        art = QRectF(rect.left(), rect.top(), rect.width(), 108)
        accent = QColor(self.game.accent)
        grad = QLinearGradient(art.left(), art.top(), art.right(), art.bottom())
        grad.setColorAt(0, QColor(accent.red(), accent.green(), accent.blue(), 60))
        grad.setColorAt(1, QColor(theme.INK))
        p.setBrush(grad)
        p.drawRoundedRect(art, 12, 12)
        p.drawRect(QRectF(art.left(), art.bottom() - 12, art.width(), 12))

        icon = pixel.load(tile(self.game.icon), 1)
        if not icon.isNull():
            size = 76 if self._hover else 68
            scaled = icon.scaled(size, size, Qt.KeepAspectRatio, Qt.FastTransformation)
            p.drawPixmap(int(art.center().x() - scaled.width() / 2),
                         int(art.center().y() - scaled.height() / 2), scaled)

        p.setFont(QFont("Noto Sans", 11, QFont.DemiBold))
        p.setPen(QColor(theme.TEXT))
        p.drawText(int(rect.left() + 14), int(art.bottom() + 28), self.game.title)

        p.setFont(QFont("Noto Sans", 8))
        p.setPen(QColor(theme.TEXT_FAINT))
        p.drawText(int(rect.left() + 14), int(art.bottom() + 46), self.game.genre)

        p.setFont(QFont("Noto Sans", 7, QFont.Bold))
        p.setPen(QColor(theme.STATE_COLORS.get(self.game.state, theme.TEXT_FAINT)))
        p.drawText(int(rect.left() + 14), int(art.bottom() + 64),
                   STATE_TEXT.get(self.game.state, ""))
        p.end()


class LibraryPage(QWidget):
    game_selected = pyqtSignal(str)

    def __init__(self, catalog, parent=None):
        super().__init__(parent)
        self.setObjectName("libraryPage")
        self.catalog = catalog

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 62, 22, 12)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = StrongBodyLabel("ALL GAMES")
        title.setStyleSheet(f"color: {theme.TEXT_DIM}; letter-spacing: 1.5px;")
        setFont(title, 11, QFont.Bold)
        header.addWidget(title)
        header.addStretch(1)

        self.search = SearchLineEdit()
        self.search.setPlaceholderText("Search your library")
        self.search.setFixedWidth(240)
        self.search.textChanged.connect(self._rebuild)
        header.addWidget(self.search)
        layout.addLayout(header)

        scroll = SingleDirectionScrollArea(orient=Qt.Vertical)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.holder = QWidget()
        self.holder.setStyleSheet("background: transparent;")
        self.flow = FlowLayout(self.holder, needAni=False)
        self.flow.setContentsMargins(0, 0, 8, 0)
        self.flow.setHorizontalSpacing(14)
        self.flow.setVerticalSpacing(14)
        scroll.setWidget(self.holder)
        layout.addWidget(scroll, 1)

        self._rebuild()

    def _rebuild(self):
        needle = self.search.text().strip().lower()
        self.flow.takeAllWidgets()
        for game in self.catalog.games:
            haystack = f"{game.title} {game.genre} {' '.join(game.tags)}".lower()
            if needle and needle not in haystack:
                continue
            card = GameCard(game)
            card.clicked.connect(self.game_selected)
            self.flow.addWidget(card)

    def refresh(self):
        self._rebuild()

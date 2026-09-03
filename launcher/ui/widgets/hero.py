"""Full-bleed hero: animated pixel art on the right, game identity on the left.

Modelled on a publisher's game page - wordmark, status chip, section links and
one big call-to-action sitting over the artwork.
"""
import webbrowser

from PyQt5.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import (QPainter, QColor, QLinearGradient, QMovie, QFont,
                         QPixmap, QFontMetrics)
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy

from qfluentwidgets import setFont

from ...core import pixel, theme
from ...core.config import cfg
from .play_button import PillButton

LINKS = [
    ("COMMUNITY", "https://pyqt-fluent-widgets.readthedocs.io/en/latest/"),
    ("SUPPORT", "https://pyqt-fluent-widgets.readthedocs.io/en/latest/"),
    ("TERMS OF USE", "https://pyqt-fluent-widgets.readthedocs.io/en/latest/"),
]

ACTION_TEXT = {
    "install": "DOWNLOAD",
    "update": "UPDATE",
    "ready": "START GAME",
    "busy": "DOWNLOADING",
    "running": "RUNNING",
    "maintenance": "UNAVAILABLE",
}

CHIP_TEXT = {
    "ready": "Installed",
    "update": "Update ready",
    "install": "Not installed",
    "busy": "Downloading",
    "running": "Playing",
    "maintenance": "Maintenance",
}


class NavLink(QLabel):
    def __init__(self, text, url, parent=None):
        super().__init__(text, parent)
        self.url = url
        self.setCursor(Qt.PointingHandCursor)
        setFont(self, 12, QFont.Normal)
        self.setStyleSheet(f"color: {theme.TEXT_DIM}; letter-spacing: 1px;")

    def enterEvent(self, event):
        self.setStyleSheet(f"color: {theme.TEXT}; letter-spacing: 1px;")

    def leaveEvent(self, event):
        self.setStyleSheet(f"color: {theme.TEXT_DIM}; letter-spacing: 1px;")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            webbrowser.open(self.url)


class StateChip(QLabel):
    """The small pill next to the wordmark, like a subscription badge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(30)
        setFont(self, 12, QFont.DemiBold)

    def set_state(self, state):
        text = CHIP_TEXT.get(state, "")
        self.setText(text)
        color = theme.STATE_COLORS.get(state, theme.TEXT_DIM)
        self.setFixedWidth(QFontMetrics(self.font()).horizontalAdvance(text) + 36)
        self.setStyleSheet(
            f"color: {color}; background-color: rgba(8, 11, 18, 0.82);"
            f"border: 1px solid {color}66; border-radius: 15px;")


class HeroSection(QWidget):
    play_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(352)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._movie = None
        self._frame = QPixmap()
        self._previous = QPixmap()
        self._prev_focus = 0.5
        self._game = None
        self._fade = 1.0

        self._fader = QVariantAnimation(self)
        self._fader.setDuration(340)
        self._fader.setEasingCurve(QEasingCurve.OutCubic)
        self._fader.valueChanged.connect(self._on_fade)

        self._build()

    # ------------------------------------------------------------------ ui

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(46, 60, 46, 26)
        layout.setSpacing(0)

        self.genre = QLabel()
        setFont(self.genre, 12, QFont.Bold)

        top = QHBoxLayout()
        top.setSpacing(16)
        self.title = QLabel()
        self.title.setFont(QFont("Noto Sans", 32, QFont.Black))
        self.title.setStyleSheet(f"color: {theme.CREAM};")
        top.addWidget(self.title, 0, Qt.AlignVCenter)

        self.chip = StateChip()
        top.addWidget(self.chip, 0, Qt.AlignVCenter)
        top.addStretch(1)

        self.subtitle = QLabel()
        setFont(self.subtitle, 13)
        self.subtitle.setStyleSheet(f"color: {theme.TEXT_DIM};")

        self.blurb = QLabel()
        self.blurb.setWordWrap(True)
        self.blurb.setFixedWidth(410)
        setFont(self.blurb, 12)
        self.blurb.setStyleSheet(f"color: {theme.TEXT_FAINT};")

        nav = QHBoxLayout()
        nav.setSpacing(0)
        self.site_link = QLabel("  ⌂  OFFICIAL WEBSITE  ")
        self.site_link.setCursor(Qt.PointingHandCursor)
        self.site_link.setFixedHeight(38)
        setFont(self.site_link, 12, QFont.DemiBold)
        self.site_link.setStyleSheet(
            f"color: {theme.TEXT}; background-color: rgba(8, 11, 18, 0.55);"
            f"border: 1px solid rgba(255,255,255,0.34);"
            f"border-radius: 19px; letter-spacing: 1px;")
        nav.addWidget(self.site_link, 0, Qt.AlignVCenter)
        nav.addSpacing(22)

        for index, (text, url) in enumerate(LINKS):
            if index:
                divider = QLabel("|")
                divider.setStyleSheet(f"color: {theme.LINE};")
                nav.addWidget(divider, 0, Qt.AlignVCenter)
                nav.addSpacing(14)
            link = NavLink(text, url)
            nav.addWidget(link, 0, Qt.AlignVCenter)
            nav.addSpacing(14)
        nav.addStretch(1)

        self.play = PillButton()
        self.play.clicked.connect(self.play_clicked)

        layout.addWidget(self.genre)
        layout.addSpacing(2)
        layout.addLayout(top)
        layout.addSpacing(4)
        layout.addWidget(self.subtitle)
        layout.addSpacing(10)
        layout.addWidget(self.blurb)
        layout.addStretch(1)
        layout.addLayout(nav)
        layout.addSpacing(20)
        layout.addWidget(self.play, 0, Qt.AlignLeft)

    # --------------------------------------------------------------- state

    def set_game(self, game, banner_path):
        first = self._game is None
        changed = first or self._game.id != game.id

        self.genre.setText(game.genre.upper())
        self.genre.setStyleSheet(f"color: {game.accent}; letter-spacing: 2px;")
        self.title.setText(game.title)
        # QLabel over-reports its width for a heavy display font, which pushes
        # the chip on top of the text; measure it and pin the width instead.
        self.title.setFixedWidth(
            QFontMetrics(self.title.font()).horizontalAdvance(game.title) + 6)
        self.subtitle.setText(game.subtitle)
        self.blurb.setText(game.blurb)
        self.set_state(game.state)

        if not changed:
            return

        self._previous = self._frame
        self._prev_focus = self._game.banner_focus if self._game else 0.5
        self._game = game

        if self._movie is not None:
            self._movie.stop()
            self._movie.deleteLater()

        self._movie = QMovie(banner_path)
        self._movie.setCacheMode(QMovie.CacheAll)
        self._movie.frameChanged.connect(self._on_frame)
        self._movie.start()
        if not cfg.get(cfg.animateBanner):
            self._movie.setPaused(True)

        self._fader.stop()
        self._fader.setStartValue(0.0)
        self._fader.setEndValue(1.0)
        self._fader.start()

    def set_state(self, state):
        self.chip.set_state(state)
        self.play.setText(ACTION_TEXT.get(state, "START GAME"))
        self.play.setEnabled(state in ("install", "update", "ready"))

    def set_animated(self, animated):
        if self._movie is not None:
            self._movie.setPaused(not animated)

    def _on_frame(self):
        self._frame = self._movie.currentPixmap()
        self.update()

    def _on_fade(self, value):
        self._fade = float(value)
        self.update()

    # -------------------------------------------------------------- paint

    def paintEvent(self, event):
        p = QPainter(self)
        rect = self.rect()
        p.fillRect(rect, QColor(theme.BASE))

        # The art occupies the right two thirds; the left is for the wordmark.
        art = QRectF(rect.width() * 0.30, 0, rect.width() * 0.70, rect.height())
        p.save()
        p.setClipRect(art)
        if not self._previous.isNull() and self._fade < 1.0:
            p.drawPixmap(art, pixel.fit(self._previous, int(art.width()),
                                        int(art.height()), self._prev_focus),
                         QRectF(0, 0, art.width(), art.height()))
        if not self._frame.isNull():
            p.setOpacity(self._fade)
            p.drawPixmap(art, pixel.fit(self._frame, int(art.width()),
                                        int(art.height()), self._game.banner_focus),
                         QRectF(0, 0, art.width(), art.height()))
            p.setOpacity(1.0)
        p.restore()

        self._paint_scrim(p, rect, art)
        p.end()

    def _paint_scrim(self, p, rect, art):
        # Fade the art into the page on every edge it touches.
        # Reaches far enough right that the nav row never lands on lit pixels.
        side = QLinearGradient(art.left(), 0, art.left() + art.width() * 0.92, 0)
        side.setColorAt(0.00, QColor(theme.BASE))
        side.setColorAt(0.40, QColor(9, 13, 21, 220))
        side.setColorAt(0.76, QColor(9, 13, 21, 70))
        side.setColorAt(1.00, QColor(9, 13, 21, 0))
        p.fillRect(art, side)

        bottom = QLinearGradient(0, rect.height() * 0.45, 0, rect.height())
        bottom.setColorAt(0.0, QColor(9, 13, 21, 0))
        bottom.setColorAt(1.0, QColor(theme.BASE))
        p.fillRect(rect, bottom)

        top = QLinearGradient(0, 0, 0, 96)
        top.setColorAt(0.0, QColor(7, 10, 17, 232))
        top.setColorAt(0.5, QColor(7, 10, 17, 120))
        top.setColorAt(1.0, QColor(7, 10, 17, 0))
        p.fillRect(rect, top)

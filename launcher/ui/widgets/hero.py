"""Full-bleed hero: animated pixel art on the right, game identity on the left.

Modelled on a publisher's game page - wordmark, status chip, section links and
one big call-to-action sitting over the artwork.
"""
import webbrowser

from PyQt5.QtCore import Qt, QRect, QVariantAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import (QPainter, QColor, QLinearGradient, QRadialGradient,
                         QMovie, QFont, QPixmap, QFontMetrics)
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
        self.setFixedWidth(QFontMetrics(self.font()).horizontalAdvance(text) + 40)
        self.setStyleSheet(
            f"color: {theme.TEXT}; background-color: rgba(255, 255, 255, 0.17);"
            f"border-radius: 15px;")


class HeroSection(QWidget):
    play_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(356)
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
        layout.setContentsMargins(48, 74, 48, 18)
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

        nav = QHBoxLayout()
        nav.setSpacing(0)
        self.site_link = QLabel("  ⌂  OFFICIAL WEBSITE  ")
        self.site_link.setCursor(Qt.PointingHandCursor)
        self.site_link.setFixedHeight(38)
        setFont(self.site_link, 12, QFont.DemiBold)
        self.site_link.setStyleSheet(
            f"color: {theme.TEXT}; border: 1px solid rgba(255,255,255,0.42);"
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
        layout.addSpacing(1)
        layout.addLayout(top)
        layout.addSpacing(22)
        layout.addLayout(nav)
        layout.addSpacing(20)
        layout.addWidget(self.play, 0, Qt.AlignLeft)
        layout.addStretch(1)

    # --------------------------------------------------------------- state

    def set_game(self, game, banner_path):
        first = self._game is None
        changed = first or self._game.id != game.id

        self.genre.setText(game.genre.upper())
        self.genre.setStyleSheet(f"color: {theme.TEXT_DIM}; letter-spacing: 2.4px;")
        self.title.setText(game.title)
        # QLabel over-reports its width for a heavy display font, which pushes
        # the chip on top of the text; measure it and pin the width instead.
        self.title.setFixedWidth(
            QFontMetrics(self.title.font()).horizontalAdvance(game.title) + 6)
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
        self._paint_ground(p, rect)

        # The art occupies the right two thirds; the left is for the wordmark.
        art = QRect(int(rect.width() * 0.34), 0,
                    int(rect.width() * 0.66), rect.height())
        if not self._previous.isNull() and self._fade < 1.0:
            p.drawPixmap(art.topLeft(),
                         self._faded(self._previous, art, self._prev_focus))
        if not self._frame.isNull():
            p.setOpacity(self._fade)
            p.drawPixmap(art.topLeft(),
                         self._faded(self._frame, art, self._game.banner_focus))
            p.setOpacity(1.0)

        self._paint_scrim(p, rect, art)
        p.end()

    @staticmethod
    def _faded(source, art, focus):
        """The artwork with its left edge masked out, so the ground shows
        through instead of being painted over."""
        layer = pixel.fit(source, art.width(), art.height(), focus)
        masked = QPixmap(layer.size())
        masked.fill(Qt.transparent)

        lp = QPainter(masked)
        lp.drawPixmap(0, 0, layer)
        lp.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        ramp = QLinearGradient(0, 0, art.width() * 0.52, 0)
        ramp.setColorAt(0.0, QColor(0, 0, 0, 0))
        ramp.setColorAt(0.55, QColor(0, 0, 0, 120))
        ramp.setColorAt(1.0, QColor(0, 0, 0, 255))
        lp.fillRect(masked.rect(), ramp)
        lp.end()
        return masked

    def _paint_ground(self, p, rect):
        """Navy page with a blue bloom sitting behind the key art."""
        p.fillRect(rect, QColor(theme.BASE))

        glow = QRadialGradient(rect.width() * 0.56, rect.height() * 0.22,
                               rect.width() * 0.58)
        glow.setColorAt(0.0, QColor(theme.GLOW))
        glow.setColorAt(0.45, QColor(48, 94, 138, 150))
        glow.setColorAt(1.0, QColor(34, 51, 73, 0))
        p.fillRect(rect, glow)

    def _paint_scrim(self, p, rect, art):
        # Fade the art into the page on every edge it touches.
        # A soft veil along the top edge. Invisible over the navy left side,
        # and enough shade for the white window controls on the right.
        top = QLinearGradient(0, 0, 0, 108)
        top.setColorAt(0.00, QColor(16, 27, 42, 248))
        top.setColorAt(0.34, QColor(16, 27, 42, 205))
        top.setColorAt(0.68, QColor(16, 27, 42, 88))
        top.setColorAt(1.00, QColor(16, 27, 42, 0))
        p.fillRect(rect, top)

        bottom = QLinearGradient(0, rect.height() * 0.62, 0, rect.height())
        bottom.setColorAt(0.0, QColor(27, 40, 57, 0))
        bottom.setColorAt(1.0, QColor(theme.BASE_LOW))
        p.fillRect(rect, bottom)

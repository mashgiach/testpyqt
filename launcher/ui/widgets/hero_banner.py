"""Animated pixel-art hero banner with the game title burned into it."""
from PyQt5.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import (QPainter, QColor, QLinearGradient, QMovie, QFont,
                         QPixmap, QFontMetrics)
from PyQt5.QtWidgets import QWidget

from ...core import pixel
from ...core import theme
from ...core.config import cfg



class HeroBanner(QWidget):
    """Draws a looping GIF scaled with nearest-neighbour, plus the title plate."""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(256)
        self.setCursor(Qt.PointingHandCursor)

        self._movie = None
        self._frame = QPixmap()
        self._previous = QPixmap()
        self._game = None
        self._fade = 1.0
        self._prev_focus = 0.5

        self._fader = QVariantAnimation(self)
        self._fader.setDuration(320)
        self._fader.setEasingCurve(QEasingCurve.OutCubic)
        self._fader.valueChanged.connect(self._on_fade)

    def set_game(self, game, banner_path: str):
        if self._game is not None and self._game.id == game.id:
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

    def set_animated(self, animated: bool):
        if self._movie is not None:
            self._movie.setPaused(not animated)

    def _on_frame(self):
        self._frame = self._movie.currentPixmap()
        self.update()

    def _on_fade(self, value):
        self._fade = float(value)
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        p.fillRect(rect, QColor(theme.INK))
        if not self._previous.isNull() and self._fade < 1.0:
            p.drawPixmap(rect, pixel.fit(self._previous, rect.width(), rect.height(), self._prev_focus))
        if not self._frame.isNull():
            p.setOpacity(self._fade)
            p.drawPixmap(rect, pixel.fit(self._frame, rect.width(), rect.height(), self._game.banner_focus))
            p.setOpacity(1.0)

        self._paint_scrim(p, rect)
        if self._game is not None:
            self._paint_plate(p, rect)
        p.end()

    def _paint_scrim(self, p, rect):
        bottom = QLinearGradient(0, rect.height() * 0.3, 0, rect.height())
        bottom.setColorAt(0.0, QColor(9, 11, 18, 0))
        bottom.setColorAt(0.55, QColor(9, 11, 18, 170))
        bottom.setColorAt(1.0, QColor(9, 11, 18, 250))
        p.fillRect(rect, bottom)

        side = QLinearGradient(0, 0, rect.width() * 0.66, 0)
        side.setColorAt(0, QColor(9, 11, 18, 225))
        side.setColorAt(1, QColor(9, 11, 18, 0))
        p.fillRect(rect, side)

    def _paint_plate(self, p, rect):
        game = self._game
        x, bottom = 34, rect.height() - 30

        p.setFont(QFont("Noto Sans", 10, QFont.Bold))
        p.setPen(QColor(game.accent))
        p.drawText(x + 2, bottom - 86, game.genre.upper())

        title_font = QFont("Noto Sans", 30, QFont.Black)
        title_font.setLetterSpacing(QFont.AbsoluteSpacing, 1.0)
        p.setFont(title_font)
        pixel.shadowed_text(p, x, bottom - 44, game.title, theme.CREAM)

        p.setFont(QFont("Noto Sans", 11))
        p.setPen(QColor(theme.TEXT_DIM))
        p.drawText(x + 2, bottom - 20, game.subtitle)

        self._paint_tags(p, x + 2, bottom - 4, game)

    def _paint_tags(self, p, x, y, game):
        font = QFont("Noto Sans", 8, QFont.Bold)
        p.setFont(font)
        fm = QFontMetrics(font)
        for tag in game.tags:
            w = fm.horizontalAdvance(tag) + 18
            box = QRectF(x, y - 15, w, 18)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 26))
            p.drawRoundedRect(box, 9, 9)
            p.setPen(QColor(theme.TEXT_DIM))
            p.drawText(box, Qt.AlignCenter, tag)
            x += w + 6

"""The primary action: a wide white pill, like the DOWNLOAD button on a
publisher's game page. Painted by hand so the hover and disabled states stay
under our control."""
from PyQt5.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QPushButton

from ...core import theme


class PillButton(QPushButton):
    def __init__(self, text="DOWNLOAD", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(268, 62)
        self.setCursor(Qt.PointingHandCursor)
        self._accent = None      # None keeps the button white
        self._hover = 0.0

        self._anim = QPropertyAnimation(self, b"hover", self)
        self._anim.setDuration(140)

    def get_hover(self):
        return self._hover

    def set_hover(self, value):
        self._hover = value
        self.update()

    hover = pyqtProperty(float, get_hover, set_hover)

    def set_accent(self, color):
        """Pass a colour to tint the pill, or None to keep it white."""
        self._accent = color
        self.update()

    def enterEvent(self, event):
        if self.isEnabled():
            self._animate(1.0)

    def leaveEvent(self, event):
        self._animate(0.0)

    def _animate(self, value):
        self._anim.stop()
        self._anim.setStartValue(self._hover)
        self._anim.setEndValue(value)
        self._anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        radius = rect.height() / 2

        if not self.isEnabled():
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 20))
            p.drawRoundedRect(rect, radius, radius)
            p.setPen(QColor(theme.TEXT_FAINT))
            self._draw_label(p, rect)
            p.end()
            return

        base = QColor(self._accent) if self._accent else QColor("#ffffff")
        if self.isDown():
            base = base.darker(112)
        elif self._hover:
            base = base.lighter(100 + int(6 * self._hover))

        # A soft halo on hover, so the pill lifts off the artwork.
        if self._hover:
            glow = QColor(base)
            glow.setAlpha(int(46 * self._hover))
            p.setPen(Qt.NoPen)
            p.setBrush(glow)
            p.drawRoundedRect(rect.adjusted(-5, -5, 5, 5), radius + 5, radius + 5)

        p.setPen(Qt.NoPen)
        p.setBrush(base)
        p.drawRoundedRect(rect, radius, radius)

        p.setPen(QColor(theme.INK if not self._accent else "#0d1018"))
        self._draw_label(p, rect)
        p.end()

    def _draw_label(self, p, rect):
        font = QFont("Noto Sans", 12, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 1.6)
        p.setFont(font)
        p.drawText(rect, Qt.AlignCenter, self.text())

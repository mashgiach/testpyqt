"""The big launch button. Painted by hand so it can carry a hard pixel edge."""
from PyQt5.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtWidgets import QPushButton

from ...core import theme


class PlayButton(QPushButton):
    def __init__(self, text="START GAME", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(226, 58)
        self.setCursor(Qt.PointingHandCursor)
        self._accent = theme.ORANGE
        self._lift = 0.0

        self._anim = QPropertyAnimation(self, b"lift", self)
        self._anim.setDuration(120)

    def get_lift(self):
        return self._lift

    def set_lift(self, value):
        self._lift = value
        self.update()

    lift = pyqtProperty(float, get_lift, set_lift)

    def set_accent(self, color: str):
        self._accent = color
        self.update()

    def enterEvent(self, event):
        if self.isEnabled():
            self._animate(1.0)

    def leaveEvent(self, event):
        self._animate(0.0)

    def _animate(self, value):
        self._anim.stop()
        self._anim.setStartValue(self._lift)
        self._anim.setEndValue(value)
        self._anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        enabled = self.isEnabled()
        base = QColor(self._accent if enabled else theme.LINE)
        edge = base.darker(160)
        pressed = self.isDown() and enabled

        depth = 5
        top = depth if pressed else int(depth - 2 * self._lift)
        face = QRectF(0, top, self.width(), self.height() - depth - top + depth)
        face.setHeight(self.height() - depth - top)

        p.setPen(Qt.NoPen)
        p.setBrush(edge)
        p.drawRoundedRect(QRectF(0, top + 4, self.width(), self.height() - top - 4), 8, 8)

        grad = QLinearGradient(0, face.top(), 0, face.bottom())
        grad.setColorAt(0, base.lighter(118 if enabled else 100))
        grad.setColorAt(1, base)
        p.setBrush(grad)
        p.drawRoundedRect(face, 8, 8)

        if enabled:
            p.setBrush(QColor(255, 255, 255, 38))
            p.drawRoundedRect(QRectF(face.left() + 6, face.top() + 4,
                                     face.width() - 12, face.height() * 0.36), 6, 6)

        font = QFont("Noto Sans", 13, QFont.Black)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2.0)
        p.setFont(font)
        p.setPen(QColor(0, 0, 0, 90))
        p.drawText(face.adjusted(0, 2, 0, 2), Qt.AlignCenter, self.text())
        p.setPen(QColor("#fff8ec" if enabled else theme.TEXT_FAINT))
        p.drawText(face, Qt.AlignCenter, self.text())
        p.end()

"""Category filter: a left-hand triangle and a label, as on the reference page."""
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPolygonF, QFontMetrics
from PyQt5.QtWidgets import QWidget

from qfluentwidgets import RoundMenu, Action, MenuAnimationType

from ...core import theme


class FilterButton(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setCursor(Qt.PointingHandCursor)
        self._label = "ALL"
        self._options = ["All"]
        self._hover = False
        self._font = QFont("Noto Sans", 12, QFont.DemiBold)
        self._font.setLetterSpacing(QFont.AbsoluteSpacing, 1.6)
        self._resize()

    def set_options(self, options):
        self._options = options
        self.set_current(options[0] if options else "All")

    def set_current(self, category):
        self._label = category.upper()
        self._resize()
        self.update()

    def text(self):
        return self._label

    def _resize(self):
        self.setFixedWidth(QFontMetrics(self._font).horizontalAdvance(self._label) + 34)

    def enterEvent(self, event):
        self._hover = True
        self.update()

    def leaveEvent(self, event):
        self._hover = False
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        menu = RoundMenu(parent=self)
        for option in self._options:
            menu.addAction(Action(option, triggered=(
                lambda checked=False, o=option: self._pick(o))))
        menu.exec(self.mapToGlobal(self.rect().bottomLeft()),
                  aniType=MenuAnimationType.DROP_DOWN)

    def _pick(self, option):
        self.set_current(option)
        self.changed.emit(option)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        color = QColor(theme.TEXT if self._hover else theme.TEXT_DIM)

        mid = self.height() / 2
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawPolygon(QPolygonF([QPointF(0, mid - 3), QPointF(10, mid - 3),
                                 QPointF(5, mid + 4)]))

        p.setFont(self._font)
        p.setPen(QColor(theme.TEXT))
        p.drawText(22, int(mid + 5), self._label)
        p.end()

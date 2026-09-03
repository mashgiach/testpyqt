"""Notice board: category tabs plus the article list."""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy

from qfluentwidgets import (Pivot, SingleDirectionScrollArea, BodyLabel, CaptionLabel,
                            StrongBodyLabel, setFont, IconWidget, FluentIcon)

from ...core import theme

CATEGORY_COLORS = {
    "Notice": theme.SKY,
    "Update": theme.ORANGE,
    "Event": theme.MOSS,
}


class NewsRow(QWidget):
    clicked = pyqtSignal(dict)

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("newsRow")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 9, 12, 9)
        layout.setSpacing(12)

        badge = CaptionLabel(item["category"].upper())
        badge.setFixedWidth(56)
        badge.setAlignment(Qt.AlignCenter)
        color = CATEGORY_COLORS.get(item["category"], theme.TEXT_DIM)
        badge.setStyleSheet(
            f"color: {color}; border: 1px solid {color}55; border-radius: 8px; padding: 2px 0;")
        setFont(badge, 10, QFont.Bold)
        layout.addWidget(badge)

        if item.get("pinned"):
            pin = IconWidget(FluentIcon.PIN)
            pin.setFixedSize(12, 12)
            layout.addWidget(pin)

        title = BodyLabel(item["title"])
        title.setStyleSheet(f"color: {theme.TEXT};")
        layout.addWidget(title, 1)

        date = CaptionLabel(item["date"])
        date.setStyleSheet(f"color: {theme.TEXT_FAINT};")
        layout.addWidget(date)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.item)


class NewsFeed(QWidget):
    article_opened = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("newsFeed")
        self._items = []
        self._filter = "All"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = StrongBodyLabel("NOTICE BOARD")
        title.setStyleSheet(f"color: {theme.TEXT_DIM}; letter-spacing: 1.5px;")
        setFont(title, 11, QFont.Bold)
        header.addWidget(title)
        header.addStretch(1)
        layout.addLayout(header)

        self.pivot = Pivot()
        for name in ("All", "Notice", "Update", "Event"):
            self.pivot.addItem(routeKey=name, text=name,
                               onClick=lambda checked=False, n=name: self.set_filter(n))
        self.pivot.setCurrentItem("All")
        pivot_row = QHBoxLayout()
        pivot_row.setContentsMargins(0, 0, 0, 0)
        pivot_row.addWidget(self.pivot)
        pivot_row.addStretch(1)
        layout.addLayout(pivot_row)

        self.scroll = SingleDirectionScrollArea(orient=Qt.Vertical)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.holder = QWidget()
        self.holder.setStyleSheet("background: transparent;")
        self.rows = QVBoxLayout(self.holder)
        self.rows.setContentsMargins(0, 0, 6, 0)
        self.rows.setSpacing(2)
        self.rows.addStretch(1)
        self.scroll.setWidget(self.holder)
        layout.addWidget(self.scroll, 1)

        self.empty = BodyLabel("Nothing posted yet.")
        self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setStyleSheet(f"color: {theme.TEXT_FAINT};")
        self.empty.setVisible(False)
        layout.addWidget(self.empty)

    def set_items(self, items):
        self._items = items
        self._rebuild()

    def set_filter(self, category):
        self._filter = category
        self._rebuild()

    def _rebuild(self):
        while self.rows.count() > 1:
            item = self.rows.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        shown = [i for i in self._items
                 if self._filter == "All" or i["category"] == self._filter]
        for index, entry in enumerate(shown):
            row = NewsRow(entry)
            row.clicked.connect(self.article_opened)
            self.rows.insertWidget(index, row)

        self.empty.setVisible(not shown)
        self.scroll.setVisible(bool(shown))

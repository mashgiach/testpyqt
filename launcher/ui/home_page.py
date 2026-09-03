"""Play tab: hero over the artwork, then the notice grid - the shape a
publisher's game page takes."""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (SingleDirectionScrollArea, TransparentDropDownPushButton,
                            RoundMenu, Action, setFont)

from .widgets.hero import HeroSection
from .widgets.news_grid import NewsGrid
from ..core import theme
from ..core.paths import banner


class HomePage(QWidget):
    article_opened = pyqtSignal(dict)
    play_clicked = pyqtSignal()

    def __init__(self, catalog, parent=None):
        super().__init__(parent)
        self.setObjectName("homePage")
        self.catalog = catalog

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.scroll = SingleDirectionScrollArea(orient=Qt.Vertical)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        outer.addWidget(self.scroll)

        holder = QWidget()
        holder.setObjectName("homeHolder")
        self.scroll.setWidget(holder)

        layout = QVBoxLayout(holder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.hero = HeroSection()
        self.hero.play_clicked.connect(self.play_clicked)
        layout.addWidget(self.hero)

        filter_row = QHBoxLayout()
        filter_row.setContentsMargins(44, 2, 46, 8)
        self.filter_btn = TransparentDropDownPushButton("ALL")
        setFont(self.filter_btn, 13, QFont.DemiBold)
        self.filter_btn.setStyleSheet(f"color: {theme.TEXT}; letter-spacing: 1.5px;")
        filter_row.addWidget(self.filter_btn)
        filter_row.addStretch(1)
        layout.addLayout(filter_row)

        grid_row = QHBoxLayout()
        grid_row.setContentsMargins(46, 0, 46, 26)
        self.grid = NewsGrid()
        self.grid.article_opened.connect(self.article_opened)
        grid_row.addWidget(self.grid, 1)
        layout.addLayout(grid_row)
        layout.addStretch(1)

    def set_game(self, game):
        self.hero.set_game(game, banner(game.banner))
        self.grid.set_game(game, self.catalog.news_for(game.id), banner(game.banner))
        self._rebuild_filter()

    def _rebuild_filter(self):
        menu = RoundMenu(parent=self.filter_btn)
        for name in self.grid.categories():
            menu.addAction(Action(name, triggered=lambda checked=False, n=name:
                                  self._apply_filter(n)))
        self.filter_btn.setMenu(menu)
        self._apply_filter("All")

    def _apply_filter(self, category):
        self.filter_btn.setText(category.upper())
        self.grid.set_filter(category)

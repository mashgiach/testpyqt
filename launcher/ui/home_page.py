"""Play tab: hero banner, notice board, server column."""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from .widgets.hero_banner import HeroBanner
from .widgets.news_feed import NewsFeed
from .widgets.side_panel import SidePanel
from ..core.paths import banner


class HomePage(QWidget):
    article_opened = pyqtSignal(dict)
    shortcut_clicked = pyqtSignal(str)

    def __init__(self, catalog, parent=None):
        super().__init__(parent)
        self.setObjectName("homePage")
        self.catalog = catalog

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.hero = HeroBanner()
        layout.addWidget(self.hero)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.news = NewsFeed()
        self.news.article_opened.connect(self.article_opened)
        body.addWidget(self.news, 1)

        self.side = SidePanel()
        self.side.shortcut_clicked.connect(self.shortcut_clicked)
        self.side.set_servers(catalog.servers)
        body.addWidget(self.side)

        layout.addLayout(body, 1)

    def set_game(self, game):
        self.hero.set_game(game, banner(game.banner))
        self.news.set_items(self.catalog.news_for(game.id))
        self.side.set_game(game)

"""The launcher window: title-bar nav, pages, and the play-button state machine."""
import random

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QVBoxLayout, QApplication,
                             QSystemTrayIcon, QMenu, QAction)

from qframelesswindow import FramelessWindow
from qfluentwidgets import (PopUpAniStackedWidget, InfoBar, InfoBarPosition,
                            setTheme, Theme, setThemeColor)

from ..core import theme as palette
from ..core.catalog import Catalog
from ..core.config import cfg
from ..core.patcher import Patcher
from ..core.paths import tile
from .widgets.title_bar import LauncherTitleBar
from .widgets.status_bar import StatusBar
from .home_page import HomePage
from .library_page import LibraryPage
from .settings_page import SettingsPage
from .dialogs import LoginDialog, ArticleDialog
from .style import STYLE_SHEET

class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.catalog = Catalog()
        self.patcher = Patcher(self)
        self.current = self.catalog.games[0]
        self._running_game = None

        self.setTitleBar(LauncherTitleBar(self))
        self.setWindowTitle("Pixel Launcher")
        self.setWindowIcon(QIcon(tile("torii")))
        self.resize(1180, 760)
        self.setMinimumSize(1080, 700)

        self._build_ui()
        self._connect()
        self._apply_style()
        self._setup_tray()

        self.select_game(self.current.id)
        self._center()

    # ---------------------------------------------------------------- layout

    def _build_ui(self):
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)

        self.stack = PopUpAniStackedWidget(self)
        self.home = HomePage(self.catalog)
        self.library = LibraryPage(self.catalog)
        self.settings = SettingsPage()
        for page in (self.home, self.library, self.settings):
            self.stack.addWidget(page)
        column.addWidget(self.stack, 1)

        self.status_bar = StatusBar()
        column.addWidget(self.status_bar)

        self.pivot = self.titleBar.pivot
        for key in ("home", "library", "settings"):
            self.pivot.widget(key).clicked.connect(
                lambda checked=False, k=key: self._go(k))
        self.titleBar.raise_()

    def _apply_style(self):
        setTheme(Theme.DARK)
        setThemeColor(palette.ACCENT)
        self.setStyleSheet(STYLE_SHEET)

    def _center(self):
        screen = QApplication.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            self.move(geo.center().x() - self.width() // 2,
                      geo.center().y() - self.height() // 2)

    # --------------------------------------------------------------- signals

    def _connect(self):
        self.library.game_selected.connect(self._open_from_library)
        self.home.article_opened.connect(self._open_article)
        self.status_bar.servers_clicked.connect(
            lambda: self.status_bar.show_servers(self.status_bar.server_btn))

        self.home.play_clicked.connect(self._on_play)
        self.status_bar.pause_clicked.connect(self._toggle_pause)
        self.status_bar.cancel_clicked.connect(self._cancel_download)
        self.status_bar.repair_clicked.connect(self._repair)

        self.patcher.stats.connect(self._on_stats)
        self.patcher.stage.connect(self._on_stage)
        self.patcher.finished.connect(self._on_download_finished)
        self.patcher.cancelled.connect(lambda _: self._refresh_current())

        self.settings.reset_requested.connect(self._reset_library)
        self.settings.animate_card.checkedChanged.connect(self.home.hero.set_animated)
        self.status_bar.set_servers(self.catalog.servers)

        self.titleBar.account.logout.connect(self.prompt_login)
        self.titleBar.account.profile.connect(
            lambda: self._toast("Account page", "This would open your profile in a browser."))
        self.titleBar.notify_btn.clicked.connect(self._show_notifications)
        self.titleBar.refresh_btn.clicked.connect(self._refresh_status)

    # ------------------------------------------------------------- behaviour

    def _go(self, key):
        self.stack.setCurrentWidget({"home": self.home, "library": self.library,
                                     "settings": self.settings}[key])
        # Over the hero the bar is transparent so the art reaches the top edge.
        # The inner pages have no art, so it takes the page's own navy and
        # scrolled content cannot slide under it.
        self.titleBar.setStyleSheet(
            "background: transparent;" if key == "home"
            else f"LauncherTitleBar {{ background-color: {palette.BASE_LOW}; }}")

    def select_game(self, game_id: str):
        self.current = self.catalog.get(game_id)
        self.home.set_game(self.current)
        self._refresh_chrome()
        if self.patcher.active and self.patcher.game_id == game_id:
            self.status_bar.show_download(self.current)
        elif self._running_game == game_id:
            self.status_bar.show_running(self.current)
        else:
            self.status_bar.show_idle(self.current)

    def _open_from_library(self, game_id: str):
        self.pivot.setCurrentItem("home")
        self._go("home")
        self.select_game(game_id)

    def _refresh_current(self):
        self.current.refresh_state()
        self._refresh_chrome()
        self.status_bar.show_idle(self.current)

    def _refresh_chrome(self):
        """Anything that shows install state: hero chip, library, status strip."""
        self.library.refresh(self.current.id)
        self.home.hero.set_state(self.current.state)
        installed = [g for g in self.catalog.games if g.installed]
        self.status_bar.set_library(len(installed), len(self.catalog.games),
                                    sum(g.size_gb for g in installed))

    def _on_play(self):
        game = self.current
        if game.state == "maintenance":
            return
        if game.state in ("install", "update"):
            self._start_download(game)
        else:
            self._launch(game)

    def _start_download(self, game):
        if self.patcher.active:
            self._toast("One download at a time",
                        "Wait for the current download to finish, or cancel it.",
                        success=False)
            return
        game.state = "busy"
        self._refresh_chrome()
        self.status_bar.show_download(game)
        self.status_bar.set_paused(False)
        self.home.hero.set_state("busy")
        self.patcher.start(game.id, game.download_gb, cfg.get(cfg.bandwidthLimit))

    def _toggle_pause(self):
        if not self.patcher.active:
            return
        if self.patcher.paused:
            self.patcher.resume()
        else:
            self.patcher.pause()
        self.status_bar.set_paused(self.patcher.paused)

    def _cancel_download(self):
        if self.patcher.active:
            self.patcher.cancel()
            self._toast("Download cancelled", f"{self.current.title} was left untouched.",
                        success=False)

    def _on_stats(self, done_gb, speed, eta):
        if self.patcher.game_id != self.current.id:
            return
        ratio = done_gb / max(self.patcher.total_gb, 0.01)
        self.status_bar.set_progress(ratio, done_gb, self.patcher.total_gb,
                                     speed, eta, self._stage_text())

    def _on_stage(self, stage):
        self._stage = stage

    def _stage_text(self):
        return getattr(self, "_stage", "Downloading game data")

    def _on_download_finished(self, game_id):
        game = self.catalog.get(game_id)
        game.installed_version = game.version
        game.refresh_state()
        self.catalog.persist()
        self._refresh_chrome()
        if game_id == self.current.id:
            self.status_bar.show_idle(game)
        self._toast("Ready to play", f"{game.title} v{game.version} is installed.")

    def _launch(self, game):
        self._running_game = game.id
        game.state = "running"
        self._refresh_chrome()
        self.home.hero.set_state("running")
        self.status_bar.show_running(game)
        self._toast("Launching", f"Starting {game.title} at {cfg.get(cfg.resolution)}.")

        if cfg.get(cfg.closeOnLaunch):
            QTimer.singleShot(900, self.hide)
        # A real launcher would spawn the game here and watch the process exit.
        QTimer.singleShot(9000, lambda: self._on_game_exit(game))

    def _on_game_exit(self, game):
        self._running_game = None
        game.refresh_state()
        self._refresh_chrome()
        if not self.isVisible():
            self.show()
        if game.id == self.current.id:
            self.status_bar.show_idle(game)
        self._toast("Session ended", f"You played {game.title} for 9 seconds. Impressive.")

    def _repair(self):
        self._toast("File check complete",
                    f"{random.randint(1180, 4200):,} files verified, nothing to repair.")

    def _reset_library(self):
        for game in self.catalog.games:
            game.installed_version = None
            game.refresh_state()
        self.catalog.persist()
        self._refresh_chrome()
        self.status_bar.show_idle(self.current)
        self._toast("Library reset", "Every game is marked as not installed.")

    def _refresh_status(self):
        for server in self.catalog.servers:
            if server["status"] != "offline":
                server["ping"] = max(8, server["ping"] + random.randint(-9, 9))
                server["load"] = min(1.0, max(0.05, server["load"] + random.uniform(-0.2, 0.2)))
        self.status_bar.set_servers(self.catalog.servers)
        self._toast("Refreshed", "Server status and notices are up to date.")

    def _open_article(self, article):
        ArticleDialog(article, self).exec()

    def _show_notifications(self):
        InfoBar.info("2 unread notices",
                     "Lantern Run starts on Friday, and Kaiju Frog is in maintenance.",
                     duration=4000, position=InfoBarPosition.TOP_RIGHT, parent=self)

    def _toast(self, title, message, success=True):
        maker = InfoBar.success if success else InfoBar.warning
        maker(title, message, duration=3500,
              position=InfoBarPosition.TOP_RIGHT, parent=self)

    # ------------------------------------------------------------- lifecycle

    def prompt_login(self):
        dialog = LoginDialog(self, cfg.get(cfg.lastAccount) if cfg.get(cfg.rememberMe) else "")
        signed_in = dialog.exec()
        if signed_in:
            name = dialog.account_name
            cfg.set(cfg.rememberMe, dialog.remember.isChecked())
            cfg.set(cfg.lastAccount, name if dialog.remember.isChecked() else "")
            self.titleBar.account.set_account(name, self.current.icon)
            self._toast("Welcome back", f"Signed in as {name}.")
        else:
            self.titleBar.account.set_account("Guest", "frog")

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = None
            return
        self.tray = QSystemTrayIcon(QIcon(tile("torii")), self)
        self.tray.setToolTip("Pixel Launcher")
        menu = QMenu(self)
        show = QAction("Show launcher", self, triggered=self._restore)
        quit_action = QAction("Quit", self, triggered=QApplication.quit)
        menu.addAction(show)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: self._restore() if reason == QSystemTrayIcon.Trigger else None)
        self.tray.show()

    def _restore(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        if cfg.get(cfg.minimizeToTray) and getattr(self, "tray", None) is not None:
            event.ignore()
            self.hide()
            self.tray.showMessage(
                "Still running",
                "Pixel Launcher kept your downloads going in the tray.",
                QSystemTrayIcon.Information, 3000)
            return
        self.catalog.persist()
        super().closeEvent(event)

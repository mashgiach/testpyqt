"""Settings tab, built from qfluentwidgets setting cards."""
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog

from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, OptionsSettingCard,
                            PushSettingCard, RangeSettingCard, HyperlinkCard,
                            PrimaryPushSettingCard, CustomColorSettingCard,
                            ExpandLayout, SingleDirectionScrollArea, FluentIcon,
                            setTheme, setThemeColor, InfoBar, InfoBarPosition)

from .. import APP_NAME, APP_VERSION, BUILD
from ..core.config import cfg, RESOLUTIONS, WINDOW_MODES, REGIONS, CONFIG_DIR

DOCS_URL = "https://pyqt-fluent-widgets.readthedocs.io/en/latest/"


class SettingsPage(QWidget):
    reset_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = SingleDirectionScrollArea(orient=Qt.Vertical)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        holder = QWidget()
        holder.setStyleSheet("background: transparent;")
        scroll.setWidget(holder)
        outer.addWidget(scroll)

        layout = ExpandLayout(holder)
        layout.setContentsMargins(48, 10, 30, 24)
        layout.setSpacing(20)

        # ExpandLayout ignores a top margin, so open the page with a spacer.
        gap = QWidget(holder)
        gap.setFixedHeight(58)
        layout.addWidget(gap)

        self.game_group = SettingCardGroup("Game", holder)
        self.install_card = PushSettingCard(
            "Change", FluentIcon.FOLDER, "Install folder",
            cfg.get(cfg.installFolder), self.game_group)
        self.install_card.clicked.connect(self._pick_folder)
        self.game_group.addSettingCard(self.install_card)

        self.game_group.addSettingCard(OptionsSettingCard(
            cfg.resolution, FluentIcon.FIT_PAGE, "Resolution",
            "Applied the next time the game starts", RESOLUTIONS, self.game_group))
        self.game_group.addSettingCard(OptionsSettingCard(
            cfg.windowMode, FluentIcon.LAYOUT, "Display mode",
            "How the game window is presented", WINDOW_MODES, self.game_group))
        self.game_group.addSettingCard(OptionsSettingCard(
            cfg.region, FluentIcon.GLOBE, "Region",
            "Picks the closest server cluster", REGIONS, self.game_group))
        layout.addWidget(self.game_group)

        self.launcher_group = SettingCardGroup("Launcher", holder)
        self.launcher_group.addSettingCard(SwitchSettingCard(
            FluentIcon.UPDATE, "Download updates automatically",
            "Patch games in the background as soon as one is published",
            cfg.autoUpdate, self.launcher_group))
        self.launcher_group.addSettingCard(SwitchSettingCard(
            FluentIcon.MINIMIZE, "Close the launcher when a game starts",
            "Frees up memory while you play", cfg.closeOnLaunch, self.launcher_group))
        self.animate_card = SwitchSettingCard(
            FluentIcon.VIDEO, "Animate the banner artwork",
            "Turn off to save a little CPU on the home screen",
            cfg.animateBanner, self.launcher_group)
        self.launcher_group.addSettingCard(self.animate_card)
        self.launcher_group.addSettingCard(SwitchSettingCard(
            FluentIcon.CHEVRON_DOWN_MED, "Minimise to the system tray",
            "Keep the launcher running after the window is closed",
            cfg.minimizeToTray, self.launcher_group))
        self.launcher_group.addSettingCard(RangeSettingCard(
            cfg.bandwidthLimit, FluentIcon.SPEED_HIGH, "Download speed limit",
            "In MB/s. Zero means no limit.", self.launcher_group))
        layout.addWidget(self.launcher_group)

        self.look_group = SettingCardGroup("Appearance", holder)
        self.theme_card = OptionsSettingCard(
            cfg.themeMode, FluentIcon.BRUSH, "Theme",
            "The launcher is designed for the dark theme",
            ["Light", "Dark", "Use system setting"], self.look_group)
        self.theme_card.optionChanged.connect(lambda item: setTheme(cfg.get(item)))
        self.look_group.addSettingCard(self.theme_card)

        self.color_card = CustomColorSettingCard(
            cfg.themeColor, FluentIcon.PALETTE, "Accent colour",
            "Used across buttons, tabs and progress bars", self.look_group)
        self.color_card.colorChanged.connect(setThemeColor)
        self.look_group.addSettingCard(self.color_card)
        layout.addWidget(self.look_group)

        self.about_group = SettingCardGroup("About", holder)
        self.about_group.addSettingCard(HyperlinkCard(
            DOCS_URL, "Open documentation", FluentIcon.HELP, "PyQt-Fluent-Widgets",
            "The widget toolkit this launcher is built on", self.about_group))
        self.about_group.addSettingCard(HyperlinkCard(
            "https://gutty-kreum.itch.io/", "Visit itch.io", FluentIcon.PHOTO, "Artwork",
            "Urban Accessories pixel pack by GuttyKreum, used with the pack's credits intact",
            self.about_group))
        self.about_group.addSettingCard(HyperlinkCard(
            "https://github.com/mashgiach/testpyqt", "Open repository", FluentIcon.CODE,
            f"{APP_NAME} {APP_VERSION}", f"Build {BUILD}", self.about_group))
        data_card = PushSettingCard(
            "Open", FluentIcon.FOLDER, "Launcher data",
            str(CONFIG_DIR), self.about_group)
        data_card.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(CONFIG_DIR))))
        self.about_group.addSettingCard(data_card)
        self.reset_card = PrimaryPushSettingCard(
            "Reset", FluentIcon.DELETE, "Reset the library",
            "Marks every game as not installed so you can watch the patcher again",
            self.about_group)
        self.reset_card.clicked.connect(self.reset_requested)
        self.about_group.addSettingCard(self.reset_card)
        layout.addWidget(self.about_group)

    def _pick_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Choose where games are installed", cfg.get(cfg.installFolder))
        if not folder or folder == cfg.get(cfg.installFolder):
            return
        cfg.set(cfg.installFolder, folder)
        self.install_card.setContent(folder)
        InfoBar.success("Install folder updated", folder, duration=3000,
                        position=InfoBarPosition.TOP_RIGHT, parent=self.window())

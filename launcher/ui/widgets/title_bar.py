"""Frameless title bar with the launcher wordmark and the account chip."""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget

from qframelesswindow import TitleBar
from qfluentwidgets import (TransparentToolButton, FluentIcon, RoundMenu, Action,
                            CaptionLabel, setFont, MenuAnimationType)

from ... import BUILD
from ...core import pixel, theme
from ...core.paths import tile


class AccountChip(QWidget):
    """Avatar plus nickname; opens the account menu on click."""

    logout = pyqtSignal()
    profile = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setCursor(Qt.PointingHandCursor)
        self._name = "Guest"
        self._avatar = "frog"
        self.setFixedWidth(150)

    def set_account(self, name: str, avatar: str = "frog"):
        self._name = name
        self._avatar = avatar
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 16))
        p.drawRoundedRect(self.rect(), 15, 15)

        icon = pixel.load(tile(self._avatar), 1)
        if not icon.isNull():
            scaled = icon.scaled(22, 22, Qt.KeepAspectRatio, Qt.FastTransformation)
            p.drawPixmap(6, (self.height() - scaled.height()) // 2, scaled)

        p.setFont(QFont("Noto Sans", 9, QFont.DemiBold))
        p.setPen(QColor(theme.TEXT))
        p.drawText(34, self.height() // 2 + 4, self._name)

        p.setPen(QColor(theme.TEXT_DIM))
        p.setFont(QFont("Noto Sans", 7))
        p.drawText(self.width() - 18, self.height() // 2 + 4, "▾")
        p.end()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        menu = RoundMenu(parent=self)
        menu.addAction(Action(FluentIcon.PEOPLE, "Account page", triggered=self.profile))
        menu.addAction(Action(FluentIcon.SHOPPING_CART, "Purchase history"))
        menu.addSeparator()
        menu.addAction(Action(FluentIcon.RETURN, "Sign out", triggered=self.logout))
        menu.exec(self.mapToGlobal(self.rect().bottomLeft()), aniType=MenuAnimationType.DROP_DOWN)


class LauncherTitleBar(TitleBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)

        mark = QLabel()
        mark.setPixmap(pixel.load(tile("torii"), 1).scaled(
            24, 24, Qt.KeepAspectRatio, Qt.FastTransformation))
        mark.setContentsMargins(14, 0, 8, 0)

        wordmark = QLabel("PIXEL")
        setFont(wordmark, 13, QFont.Black)
        wordmark.setStyleSheet(f"color: {theme.CREAM}; letter-spacing: 2px;")

        suffix = QLabel("LAUNCHER")
        setFont(suffix, 13, QFont.Light)
        suffix.setStyleSheet(f"color: {theme.ORANGE}; letter-spacing: 2px;")

        self.build = CaptionLabel(f"build {BUILD}")
        self.build.setStyleSheet(f"color: {theme.TEXT_FAINT};")
        self.build.setContentsMargins(14, 2, 0, 0)

        self.account = AccountChip(self)

        self.notify_btn = TransparentToolButton(FluentIcon.RINGER, self)
        self.notify_btn.setFixedSize(34, 30)

        left = QHBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(2)
        for widget in (mark, wordmark, suffix, self.build):
            left.addWidget(widget, 0, Qt.AlignVCenter)

        # The base title bar already ends with a stretch and the window buttons,
        # so the account controls go in just ahead of the minimise button.
        self.hBoxLayout.insertLayout(0, left)
        slot = self.hBoxLayout.indexOf(self.minBtn)
        self.hBoxLayout.insertWidget(slot, self.notify_btn, 0, Qt.AlignVCenter)
        self.hBoxLayout.insertSpacing(slot + 1, 6)
        self.hBoxLayout.insertWidget(slot + 2, self.account, 0, Qt.AlignVCenter)
        self.hBoxLayout.insertSpacing(slot + 3, 12)

        self.maxBtn.setVisible(False)
        for btn in (self.minBtn, self.closeBtn):
            btn.setHoverColor(Qt.white)
            btn.setPressedColor(Qt.white)
        self.minBtn.setHoverBackgroundColor(QColor(255, 255, 255, 26))
        self.minBtn.setPressedBackgroundColor(QColor(255, 255, 255, 40))
        self.closeBtn.setHoverBackgroundColor(QColor(212, 103, 107))
        self.closeBtn.setPressedBackgroundColor(QColor(180, 82, 86))

    def mouseDoubleClickEvent(self, event):
        event.ignore()  # no maximise; the launcher is a fixed-size window

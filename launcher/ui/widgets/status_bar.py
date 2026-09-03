"""Slim bottom strip: server health, download readout, library size.

The primary action lives up in the hero now, so this bar only reports.
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from qfluentwidgets import (ProgressBar, TransparentToolButton, FluentIcon,
                            CaptionLabel, setFont, ToolTipFilter, Flyout,
                            FlyoutViewBase)
from PyQt5.QtWidgets import QVBoxLayout

from ...core import theme


def human_eta(seconds: int) -> str:
    if seconds <= 0:
        return "--:--"
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class ServerFlyoutView(FlyoutViewBase):
    def __init__(self, servers, parent=None):
        super().__init__(parent)
        from .side_panel import ServerRow

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(0)

        heading = CaptionLabel("SERVER STATUS")
        heading.setStyleSheet(f"color: {theme.TEXT_DIM}; letter-spacing: 1.5px;")
        setFont(heading, 11, QFont.Bold)
        layout.addWidget(heading)
        layout.addSpacing(6)

        for server in servers:
            row = ServerRow(server)
            row.setFixedWidth(260)
            layout.addWidget(row)


class StatusBar(QWidget):
    pause_clicked = pyqtSignal()
    cancel_clicked = pyqtSignal()
    repair_clicked = pyqtSignal()
    servers_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setFixedHeight(46)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 18, 0)
        layout.setSpacing(14)

        self.server_btn = QLabel()
        self.server_btn.setCursor(Qt.PointingHandCursor)
        setFont(self.server_btn, 11)
        self.server_btn.mouseReleaseEvent = lambda event: self.servers_clicked.emit()
        layout.addWidget(self.server_btn)

        self.status = CaptionLabel("")
        self.status.setStyleSheet(f"color: {theme.TEXT_DIM};")
        self.status.setMinimumWidth(190)
        setFont(self.status, 11)
        layout.addWidget(self.status)

        self.bar = ProgressBar()
        self.bar.setFixedHeight(4)
        self.bar.setFixedWidth(150)
        self.bar.setVisible(False)
        layout.addWidget(self.bar)

        self.detail = CaptionLabel("")
        self.detail.setStyleSheet(f"color: {theme.TEXT_FAINT};")
        self.detail.setMinimumWidth(230)
        setFont(self.detail, 11)
        layout.addWidget(self.detail)

        layout.addStretch(1)

        self.pause_btn = TransparentToolButton(FluentIcon.PAUSE)
        self.pause_btn.setToolTip("Pause download")
        self.pause_btn.setVisible(False)
        self.pause_btn.clicked.connect(self.pause_clicked)

        self.cancel_btn = TransparentToolButton(FluentIcon.CLOSE)
        self.cancel_btn.setToolTip("Cancel download")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_clicked)

        self.repair_btn = TransparentToolButton(FluentIcon.SYNC)
        self.repair_btn.setToolTip("Verify and repair files")
        self.repair_btn.clicked.connect(self.repair_clicked)

        for btn in (self.pause_btn, self.cancel_btn, self.repair_btn):
            btn.setFixedSize(30, 30)
            btn.installEventFilter(ToolTipFilter(btn))
            layout.addWidget(btn)

        self.library = CaptionLabel("")
        self.library.setStyleSheet(f"color: {theme.TEXT_FAINT};")
        setFont(self.library, 11)
        layout.addWidget(self.library)

    # ------------------------------------------------------------- updates

    def set_servers(self, servers):
        self._servers = servers
        best = min((s for s in servers if s["status"] == "online"),
                   key=lambda s: s["ping"], default=None)
        if best is None:
            self.server_btn.setText("All servers offline")
            self.server_btn.setStyleSheet(f"color: {theme.ROSE};")
            return
        self.server_btn.setText(f"●  {best['ping']} ms")
        self.server_btn.setStyleSheet(f"color: {theme.MOSS};")

    def show_servers(self, target):
        Flyout.make(ServerFlyoutView(self._servers, target), target, target.window())

    def set_library(self, installed, total, gigabytes):
        self.library.setText(f"{installed} of {total} installed  ·  {gigabytes:.1f} GB")

    def show_idle(self, game):
        self.bar.setVisible(False)
        self.library.setVisible(True)
        self.pause_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.repair_btn.setVisible(game.installed)
        self.detail.setText("")

        if game.state == "maintenance":
            self.status.setText("Under maintenance — servers return at 06:00 JST")
        elif game.state == "update":
            self.status.setText(
                f"v{game.installed_version} installed · v{game.version} available "
                f"({game.patch_gb:.1f} GB)")
        elif game.state == "install":
            self.status.setText(f"Not installed · {game.size_gb:.1f} GB required")
        else:
            self.status.setText(f"v{game.version} · {game.players:,} players online")

    def show_running(self, game):
        self.bar.setVisible(False)
        self.library.setVisible(True)
        self.pause_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.repair_btn.setVisible(False)
        self.detail.setText("")
        self.status.setText(f"{game.title} is running")

    def show_download(self, game):
        self.bar.setVisible(True)
        self.bar.setValue(0)
        self.pause_btn.setVisible(True)
        self.cancel_btn.setVisible(True)
        self.repair_btn.setVisible(False)
        self.library.setVisible(False)
        self.status.setText("Preparing download")
        self.detail.setText("")

    def set_progress(self, ratio, done_gb, total_gb, speed, eta, stage):
        self.bar.setValue(int(ratio * 100))
        self.status.setText(f"{stage} · {ratio * 100:.0f}%")
        if speed > 1:
            self.detail.setText(
                f"{done_gb:.1f} / {total_gb:.1f} GB · {speed:.0f} MB/s · {human_eta(eta)} left")
        else:
            self.detail.setText(f"{done_gb:.1f} / {total_gb:.1f} GB · paused")

    def set_paused(self, paused):
        self.pause_btn.setIcon(FluentIcon.PLAY if paused else FluentIcon.PAUSE)
        self.pause_btn.setToolTip("Resume download" if paused else "Pause download")

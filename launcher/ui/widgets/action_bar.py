"""Bottom bar: install state, download readout, and the launch button."""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from qfluentwidgets import (ProgressBar, TransparentToolButton, FluentIcon,
                            CaptionLabel, StrongBodyLabel, setFont, ToolTipFilter)

from ...core import theme
from .play_button import PlayButton


def human_eta(seconds: int) -> str:
    if seconds <= 0:
        return "--:--"
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class ActionBar(QWidget):
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    cancel_clicked = pyqtSignal()
    repair_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("actionBar")
        self.setFixedHeight(96)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(18)

        self.status = StrongBodyLabel("Ready to play")
        setFont(self.status, 14, QFont.DemiBold)

        self.detail = CaptionLabel("")
        self.detail.setStyleSheet(f"color: {theme.TEXT_DIM};")

        self.bar = ProgressBar()
        self.bar.setFixedHeight(6)
        self.bar.setVisible(False)

        info = QVBoxLayout()
        info.setSpacing(6)
        info.addStretch(1)
        info.addWidget(self.status)
        info.addWidget(self.bar)
        info.addWidget(self.detail)
        info.addStretch(1)
        layout.addLayout(info, 1)

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
            btn.installEventFilter(ToolTipFilter(btn))
            layout.addWidget(btn)

        self.play = PlayButton()
        self.play.clicked.connect(self.play_clicked)
        layout.addWidget(self.play)

    def show_idle(self, game):
        self.bar.setVisible(False)
        self.pause_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.repair_btn.setVisible(game.installed)
        self.play.setEnabled(game.state != "maintenance")
        self.play.set_accent(game.accent)
        self.play.setText(game.action_label)

        if game.state == "maintenance":
            self.status.setText("Under maintenance")
            self.detail.setText("Servers are expected back at 06:00 JST")
        elif game.state == "update":
            self.status.setText(f"Update available - v{game.version}")
            self.detail.setText(
                f"You have v{game.installed_version} - {game.patch_gb:.1f} GB to download")
        elif game.state == "install":
            self.status.setText("Not installed")
            self.detail.setText(f"{game.size_gb:.1f} GB required on disk")
        else:
            self.status.setText(f"Ready to play - v{game.version}")
            self.detail.setText(f"{game.players:,} players online right now")

    def show_running(self, game):
        self.bar.setVisible(False)
        self.pause_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.repair_btn.setVisible(False)
        self.play.setEnabled(False)
        self.play.setText("RUNNING")
        self.status.setText(f"{game.title} is running")
        self.detail.setText("The launcher will stay open in the background")

    def show_download(self, game):
        self.bar.setVisible(True)
        self.bar.setValue(0)
        self.pause_btn.setVisible(True)
        self.cancel_btn.setVisible(True)
        self.repair_btn.setVisible(False)
        self.play.setEnabled(False)
        self.play.setText("DOWNLOADING")
        self.status.setText("Preparing download")
        self.detail.setText("")

    def set_progress(self, ratio: float, done_gb: float, total_gb: float,
                     speed: float, eta: int, stage: str):
        self.bar.setValue(int(ratio * 100))
        self.status.setText(f"{stage} - {ratio * 100:.0f}%")
        if speed > 1:
            self.detail.setText(
                f"{done_gb:.1f} / {total_gb:.1f} GB   -   {speed:.0f} MB/s   -   {human_eta(eta)} left")
        else:
            self.detail.setText(f"{done_gb:.1f} / {total_gb:.1f} GB   -   paused")

    def set_paused(self, paused: bool):
        self.pause_btn.setIcon(FluentIcon.PLAY if paused else FluentIcon.PAUSE)
        self.pause_btn.setToolTip("Resume download" if paused else "Pause download")

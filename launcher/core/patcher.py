"""Simulated patch downloader.

Stands in for a real CDN client: it emits the same signals a genuine
downloader would, so the UI can be pointed at real work later. The only
fiction is `_duration_for` — swap that for actual byte counts and the rest
of the class keeps working.
"""
import math
import random

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

TICK_MS = 100
MAX_DEMO_SECONDS = 75


class Patcher(QObject):
    progress = pyqtSignal(float)           # 0..1
    stats = pyqtSignal(float, float, int)  # done_gb, speed_mbs, eta_seconds
    stage = pyqtSignal(str)                # human readable phase
    finished = pyqtSignal(str)             # game id
    cancelled = pyqtSignal(str)            # game id

    STAGES = [
        (0.00, "Checking file integrity"),
        (0.06, "Downloading game data"),
        (0.84, "Verifying downloaded files"),
        (0.93, "Applying patch"),
        (0.99, "Finishing up"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.game_id = None
        self.total_gb = 0.0
        self.done_gb = 0.0
        self.speed = 0.0
        self.paused = False
        self._rate = 0.0     # GB per second
        self._stage = ""
        self._timer = QTimer(self)
        self._timer.setInterval(TICK_MS)
        self._timer.timeout.connect(self._tick)

    @property
    def active(self) -> bool:
        return self.game_id is not None

    @staticmethod
    def _duration_for(total_gb: float) -> float:
        """Keep every download watchable: bigger ones take longer, but not much."""
        return 10 + 4 * math.sqrt(total_gb)

    def start(self, game_id: str, total_gb: float, limit_mbs: int = 0):
        self.game_id = game_id
        self.total_gb = max(total_gb, 0.1)
        self.done_gb = 0.0
        self.paused = False
        self._stage = ""

        self._rate = self.total_gb / self._duration_for(self.total_gb)
        if limit_mbs:
            # A throttle the user set actually slows things down, up to a point.
            self._rate = max(min(self._rate, limit_mbs / 1024),
                             self.total_gb / MAX_DEMO_SECONDS)
        self.speed = self._rate * 1024
        self._timer.start()

    def pause(self):
        self.paused = True
        self.speed = 0.0
        self.stage.emit("Paused")
        self._emit_stats()

    def resume(self):
        self.paused = False
        self.stage.emit(self._stage)

    def cancel(self):
        self._timer.stop()
        stopped, self.game_id = self.game_id, None
        self.done_gb = 0.0
        self.speed = 0.0
        self.progress.emit(0.0)
        if stopped:
            self.cancelled.emit(stopped)

    def _tick(self):
        if self.paused:
            return

        # Jitter the wire speed a little so the readout looks alive.
        self.speed = self._rate * 1024 * random.uniform(0.86, 1.12)
        self.done_gb = min(self.total_gb, self.done_gb + self.speed / 1024 * TICK_MS / 1000)

        ratio = self.done_gb / self.total_gb
        for threshold, label in reversed(self.STAGES):
            if ratio >= threshold:
                if label != self._stage:
                    self._stage = label
                    self.stage.emit(label)
                break

        self.progress.emit(ratio)
        self._emit_stats()

        if self.done_gb >= self.total_gb:
            self._timer.stop()
            done_id, self.game_id = self.game_id, None
            self.finished.emit(done_id)

    def _emit_stats(self):
        remaining = max(0.0, self.total_gb - self.done_gb)
        eta = int(remaining * 1024 / self.speed) if self.speed > 1 else 0
        self.stats.emit(self.done_gb, self.speed, eta)

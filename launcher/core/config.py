"""Persisted launcher settings, backed by qfluentwidgets' QConfig."""
import json
import os
from pathlib import Path

from qfluentwidgets import (QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator, qconfig)

# PIXEL_LAUNCHER_HOME lets you keep settings beside a portable install, and
# gives the tests somewhere disposable to write.
CONFIG_DIR = Path(os.environ.get("PIXEL_LAUNCHER_HOME",
                                 Path.home() / ".pixel-launcher"))
CONFIG_FILE = CONFIG_DIR / "config.json"
STATE_FILE = CONFIG_DIR / "library.json"

RESOLUTIONS = ["1280x720", "1600x900", "1920x1080", "2560x1440", "3840x2160"]
WINDOW_MODES = ["Fullscreen", "Borderless", "Windowed"]
REGIONS = ["Kanagawa", "Shibuya", "Global"]


class Config(QConfig):
    installFolder = ConfigItem("Game", "InstallFolder", str(Path.home() / "Games"))
    resolution = OptionsConfigItem("Game", "Resolution", "1920x1080", OptionsValidator(RESOLUTIONS))
    windowMode = OptionsConfigItem("Game", "WindowMode", "Borderless", OptionsValidator(WINDOW_MODES))
    region = OptionsConfigItem("Game", "Region", "Kanagawa", OptionsValidator(REGIONS))

    autoUpdate = ConfigItem("Launcher", "AutoUpdate", True, BoolValidator())
    closeOnLaunch = ConfigItem("Launcher", "CloseOnLaunch", False, BoolValidator())
    animateBanner = ConfigItem("Launcher", "AnimateBanner", True, BoolValidator())
    minimizeToTray = ConfigItem("Launcher", "MinimizeToTray", True, BoolValidator())
    bandwidthLimit = RangeConfigItem("Launcher", "BandwidthLimit", 0, RangeValidator(0, 200))

    rememberMe = ConfigItem("Account", "RememberMe", True, BoolValidator())
    lastAccount = ConfigItem("Account", "LastAccount", "")


cfg = Config()
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
qconfig.load(str(CONFIG_FILE), cfg)


def load_library_state() -> dict:
    """Which games are installed, and at what version."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_library_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

"""Filesystem layout for the launcher."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
TILES = ASSETS / "tiles"
BANNERS = ASSETS / "banners"
DATA = ROOT / "data"


def tile(name: str) -> str:
    return str(TILES / f"{name}.png")


def banner(name: str) -> str:
    return str(BANNERS / name)

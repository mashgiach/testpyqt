"""Palette lifted from the GuttyKreum pixel art, pitched dark for the launcher."""

# Near-black navy base. The art carries the colour; the chrome stays out of it.
INK = "#05070c"
BASE = "#090d15"
SURFACE = "#0f141f"
SURFACE_HI = "#161d2b"
LINE = "#1b2434"

# Deep blue the hero scrim fades into, matching the tileset's night sky.
HERO_SCRIM = "#070b14"

# Accents pulled straight out of the sprites.
ORANGE = "#e8703a"
ORANGE_DIM = "#b4522a"
SKY = "#7fb2e5"
STEEL = "#4a6a9a"
CREAM = "#f2e7d3"
MOSS = "#7aa886"
ROSE = "#d4676b"

TEXT = "#eef2fa"
TEXT_DIM = "#8e99b3"
TEXT_FAINT = "#5c6782"

STATE_COLORS = {
    "ready": MOSS,
    "update": ORANGE,
    "install": SKY,
    "busy": SKY,
    "running": MOSS,
    "maintenance": ROSE,
}

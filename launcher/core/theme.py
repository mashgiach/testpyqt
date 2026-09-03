"""Palette matched to the reference game page: deep navy blue, not black."""

# One family of navies, so nothing meets in a hard line. The page is navy,
# the art sits in a blue glow, and the chrome is the same hue a shade down.
INK = "#18263a"
BASE = "#223349"
BASE_LOW = "#1b2839"
SURFACE = "#182739"
SURFACE_HI = "#213248"
LINE = "#2c3d55"

# The cyan-blue bloom behind the key art.
GLOW = "#3b6f9e"
SCRIM = "#1d2c40"

# The UI accent is the page's own blue. The sprite colours below are for
# game identity and status only - they never tint the chrome.
ACCENT = "#7fb2e5"

ORANGE = "#e8703a"
ORANGE_DIM = "#b4522a"
SKY = "#7fb2e5"
STEEL = "#4a6a9a"
CREAM = "#f2e7d3"
MOSS = "#7aa886"
ROSE = "#d4676b"

TEXT = "#f2f5fa"
TEXT_DIM = "#94a1b5"
TEXT_FAINT = "#6c7b91"

STATE_COLORS = {
    "ready": MOSS,
    "update": ORANGE,
    "install": SKY,
    "busy": SKY,
    "running": MOSS,
    "maintenance": ROSE,
}

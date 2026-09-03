"""Helpers for drawing pixel art without the blur.

Every scale in here goes through FastTransformation, so a 32x32 sprite blown
up to 64px keeps its hard edges instead of turning to mush.
"""
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QColor

_cache: dict = {}


def load(path: str, scale: int = 1) -> QPixmap:
    key = (path, scale)
    if key not in _cache:
        pm = QPixmap(path)
        if not pm.isNull() and scale != 1:
            pm = pm.scaled(pm.width() * scale, pm.height() * scale,
                           Qt.KeepAspectRatio, Qt.FastTransformation)
        _cache[key] = pm
    return _cache[key]


def fit(pm: QPixmap, w: int, h: int, focus: float = 0.5,
        hfocus: float = 0.5) -> QPixmap:
    """Scale a sprite to fill w*h, cropping the overflow, pixels intact.

    `focus` biases the vertical crop and `hfocus` the horizontal one: 0 keeps
    the top/left edge, 1 keeps the bottom/right.
    """
    if pm.isNull() or w <= 0 or h <= 0:
        return pm
    factor = max(w / pm.width(), h / pm.height())
    tw, th = max(1, round(pm.width() * factor)), max(1, round(pm.height() * factor))
    big = pm.scaled(tw, th, Qt.IgnoreAspectRatio, Qt.FastTransformation)
    return big.copy(QRect(round((tw - w) * hfocus), round((th - h) * focus), w, h))


def tinted(pm: QPixmap, color: str, strength: float = 1.0) -> QPixmap:
    out = QPixmap(pm.size())
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.drawPixmap(0, 0, pm)
    p.setCompositionMode(QPainter.CompositionMode_SourceIn)
    c = QColor(color)
    c.setAlphaF(strength)
    p.fillRect(out.rect(), c)
    p.end()
    return out


def shadowed_text(painter: QPainter, x: int, y: int, text: str,
                  color: str, shadow: str = "#0b0e17", offset: int = 3):
    """Hard offset shadow — the retro way, no soft blur."""
    painter.setPen(QColor(shadow))
    painter.drawText(x + offset, y + offset, text)
    painter.setPen(QColor(color))
    painter.drawText(x, y, text)

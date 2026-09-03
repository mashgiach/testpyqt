"""Notice grid, laid out like the reference game page: four tall cards across.

Two card shapes, as on the page it is modelled on - promo posts are pure
artwork, and ordinary notices put a smaller image over a text body.
"""
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QMovie, QLinearGradient
from PyQt5.QtWidgets import QWidget

from ...core import pixel, theme
from ...core.paths import tile

CATEGORY_COLORS = {
    "Notice": theme.SKY,
    "Update": theme.ORANGE,
    "Event": theme.MOSS,
    "Sales": theme.CREAM,
}

CATEGORY_SPRITES = {
    "Update": ["sign_neon", "machine", "arcade"],
    "Event": ["food_cart", "fan", "drone"],
    "Notice": ["board", "post", "kiosk"],
    "Sales": ["vending", "kiosk"],
}

CARD_W, CARD_H, ART_H, GAP = 257, 270, 118, 18
COLUMNS = 4


class NewsCard(QWidget):
    clicked = pyqtSignal(dict)

    def __init__(self, item, art, focus, hfocus, accent, sprite, parent=None):
        super().__init__(parent)
        self.item = item
        self.art = art
        self.focus = focus
        self.hfocus = hfocus
        self.accent = accent
        self.sprite = sprite
        self.featured = bool(item.get("featured"))
        self.tint = CATEGORY_COLORS.get(item["category"], accent)
        self.setFixedSize(CARD_W, CARD_H)
        self.setCursor(Qt.PointingHandCursor)
        self._lift = 0.0

        self._anim = QPropertyAnimation(self, b"lift", self)
        self._anim.setDuration(150)

    def get_lift(self):
        return self._lift

    def set_lift(self, value):
        self._lift = value
        self.update()

    lift = pyqtProperty(float, get_lift, set_lift)

    def enterEvent(self, event):
        self._animate(1.0)

    def leaveEvent(self, event):
        self._animate(0.0)

    def _animate(self, value):
        self._anim.stop()
        self._anim.setStartValue(self._lift)
        self._anim.setEndValue(value)
        self._anim.start()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.item)

    # -------------------------------------------------------------- paint

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(0, -3 * self._lift, self.width(), self.height())

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(theme.SURFACE_HI if self._lift else theme.SURFACE))
        p.drawRect(rect)

        if self.featured:
            self._paint_poster(p, rect)
        else:
            self._paint_art(p, QRectF(rect.left(), rect.top(), rect.width(), ART_H))
            self._paint_body(p, rect)
        p.end()

    def _draw_art(self, p, art_rect, focus, hfocus, darken):
        p.save()
        p.setClipRect(art_rect)
        if not self.art.isNull():
            p.drawPixmap(art_rect, pixel.fit(self.art, int(art_rect.width()),
                                             int(art_rect.height()), focus, hfocus),
                         QRectF(0, 0, art_rect.width(), art_rect.height()))
        p.fillRect(art_rect, QColor(21, 30, 44, darken))
        tint = QColor(self.tint)
        tint.setAlpha(46)
        p.fillRect(art_rect, tint)
        p.restore()

    def _paint_art(self, p, art_rect):
        self._draw_art(p, art_rect, self.focus, self.hfocus, 168)

        if not self.sprite.isNull():
            side = 74 if self._lift else 68
            scaled = self.sprite.scaled(side, side, Qt.KeepAspectRatio,
                                        Qt.FastTransformation)
            p.drawPixmap(int(art_rect.center().x() - scaled.width() / 2),
                         int(art_rect.center().y() - scaled.height() / 2 - 2), scaled)

        fade = QLinearGradient(0, art_rect.bottom() - 40, 0, art_rect.bottom())
        fade.setColorAt(0.0, QColor(21, 30, 44, 0))
        fade.setColorAt(1.0, QColor(theme.SURFACE))
        p.fillRect(art_rect, fade)

        if self._lift:
            p.setBrush(QColor(255, 255, 255, int(16 * self._lift)))
            p.drawRect(art_rect)

    def _paint_poster(self, p, rect):
        """A promo post: artwork edge to edge, title burned into the bottom."""
        self._draw_art(p, rect, self.focus, self.hfocus, 58)

        veil = QLinearGradient(0, rect.top() + rect.height() * 0.42, 0, rect.bottom())
        veil.setColorAt(0.0, QColor(12, 19, 30, 0))
        veil.setColorAt(0.55, QColor(12, 19, 30, 175))
        veil.setColorAt(1.0, QColor(12, 19, 30, 246))
        p.fillRect(rect, veil)

        media = bool(self.item.get("media"))
        bottom = rect.bottom() - (50 if media else 20)
        x, width = rect.left() + 18, int(rect.width() - 36)

        p.setFont(QFont("Noto Sans", 8, QFont.Bold))
        p.setPen(QColor(theme.TEXT))
        p.drawText(int(x), int(bottom - 52), self.item["category"].upper())

        p.setPen(QColor(theme.TEXT))
        self._draw_wrapped(p, QFont("Noto Sans", 12, QFont.DemiBold),
                           self.item["title"], x, bottom - 24, width, 2, 20)

        if media:
            self._paint_media_strip(p, rect)

    def _paint_media_strip(self, p, rect):
        strip = QRectF(rect.left(), rect.bottom() - 34, rect.width(), 34)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(12, 19, 30, 232))
        p.drawRect(strip)

        font = QFont("Noto Sans", 9, QFont.Bold)
        p.setFont(font)
        p.setPen(QColor(theme.TEXT))
        label = "MEDIA"
        text_w = QFontMetrics(font).horizontalAdvance(label)
        p.drawText(int(strip.center().x() - text_w / 2), int(strip.center().y() + 4), label)

        # Two offset outlines, the usual shorthand for a stack of images.
        icon_x, icon_y = strip.right() - 30, strip.center().y() - 5
        p.setBrush(Qt.NoBrush)
        p.setPen(QColor(theme.TEXT_DIM))
        p.drawRect(QRectF(icon_x + 3, icon_y - 3, 11, 9))
        p.drawRect(QRectF(icon_x, icon_y, 11, 9))

    def _paint_body(self, p, rect):
        x = rect.left() + 18
        width = int(rect.width() - 36)
        date_baseline = rect.bottom() - 20
        y = rect.top() + ART_H + 24

        p.setFont(QFont("Noto Sans", 8, QFont.Bold))
        p.setPen(QColor(theme.TEXT))
        p.drawText(int(x), int(y), self.item["category"].upper())

        p.setPen(QColor(theme.TEXT))
        y = self._draw_wrapped(p, QFont("Noto Sans", 12, QFont.DemiBold),
                               self.item["title"], x, y + 26, width, 2, 19) + 19

        room = int((date_baseline - 12 - y) // 16)
        if room > 0:
            p.setPen(QColor(theme.TEXT_DIM))
            self._draw_wrapped(p, QFont("Noto Sans", 10), self.item["body"],
                               x, y + 15, width, min(room, 3), 16)

        p.setFont(QFont("Noto Sans", 9))
        p.setPen(QColor(theme.TEXT_FAINT))
        p.drawText(int(x), int(date_baseline), self.item["date"])

    @staticmethod
    def _draw_wrapped(p, font, text, x, y, width, max_lines, line_height):
        """Draw at most `max_lines` of text, eliding the last one.

        Returns the baseline of the final line drawn.
        """
        p.setFont(font)
        fm = QFontMetrics(font)
        lines, line, leftover = [], "", False
        for word in text.split():
            candidate = f"{line} {word}".strip()
            if fm.horizontalAdvance(candidate) <= width:
                line = candidate
                continue
            if line:
                lines.append(line)
            line = word
            if len(lines) == max_lines:
                leftover = True
                break
        else:
            if line:
                lines.append(line)

        if leftover and lines:
            lines[-1] = fm.elidedText(lines[-1] + " ...", Qt.ElideRight, width)

        for entry in lines:
            p.drawText(int(x), int(y), entry)
            y += line_height
        return y - line_height


class NewsGrid(QWidget):
    article_opened = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._filter = "All"
        self._game = None
        self._art = None
        self._cards = []
        self.setFixedWidth(COLUMNS * CARD_W + (COLUMNS - 1) * GAP)
        self.setMinimumHeight(CARD_H)

    def set_game(self, game, items, banner_path):
        self._game = game
        self._items = items
        # One still frame is enough for the cards; the hero does the animating.
        movie = QMovie(banner_path)
        movie.jumpToFrame(0)
        self._art = movie.currentPixmap()
        self._rebuild()

    def set_filter(self, category):
        self._filter = category
        self._rebuild()

    def categories(self):
        return ["All"] + sorted({i["category"] for i in self._items})

    def _rebuild(self):
        for card in self._cards:
            card.deleteLater()
        self._cards = []

        shown = [i for i in self._items
                 if self._filter == "All" or i["category"] == self._filter]
        for index, entry in enumerate(shown):
            # Walk the crop across and down the artwork so no two cards match.
            focus = (0.10 + 0.23 * index) % 1.0
            hfocus = (0.5 + 0.31 * index) % 1.0
            if entry.get("featured"):
                sprite = pixel.load(tile(self._game.icon))
            else:
                names = CATEGORY_SPRITES.get(entry["category"], [self._game.icon])
                sprite = pixel.load(tile(names[index % len(names)]))
            card = NewsCard(entry, self._art, focus, hfocus,
                            self._game.accent, sprite, self)
            card.clicked.connect(self.article_opened)
            card.show()
            self._cards.append(card)
        self._relayout()

    def resizeEvent(self, event):
        self._relayout()

    def _relayout(self):
        if not self._cards:
            self.setMinimumHeight(0)
            return
        for index, card in enumerate(self._cards):
            row, column = divmod(index, COLUMNS)
            card.move(column * (CARD_W + GAP), row * (CARD_H + GAP))
        rows = (len(self._cards) + COLUMNS - 1) // COLUMNS
        self.setMinimumHeight(rows * (CARD_H + GAP) - GAP)

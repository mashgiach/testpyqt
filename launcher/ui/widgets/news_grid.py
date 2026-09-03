"""Notice grid: image-topped cards, like a publisher's news feed."""
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QMovie, QLinearGradient
from PyQt5.QtWidgets import QWidget

from ...core import pixel, theme
from ...core.paths import tile

CATEGORY_COLORS = {
    "Notice": theme.SKY,
    "Update": theme.ORANGE,
    "Event": theme.MOSS,
}

CATEGORY_SPRITES = {
    "Update": ["sign_neon", "machine", "arcade"],
    "Event": ["food_cart", "fan", "drone"],
    "Notice": ["board", "post", "kiosk"],
    "Sales": ["vending", "kiosk"],
}

CARD_W, CARD_H, ART_H, GAP = 198, 240, 112, 16


class NewsCard(QWidget):
    """One notice. The art is a slice of the game's banner, offset per card so
    a row of cards never shows the same crop twice."""

    clicked = pyqtSignal(dict)

    def __init__(self, item, art, focus, hfocus, accent, sprite, parent=None):
        super().__init__(parent)
        self.item = item
        self.art = art
        self.focus = focus
        self.hfocus = hfocus
        self.accent = accent
        self.sprite = sprite
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

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        offset = -3 * self._lift
        rect = QRectF(0, offset, self.width(), self.height() - 1)

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(theme.SURFACE_HI if self._lift else theme.SURFACE))
        p.drawRoundedRect(rect, 6, 6)

        self._paint_art(p, QRectF(rect.left(), rect.top(), rect.width(), ART_H))
        self._paint_body(p, rect)
        p.end()

    def _paint_art(self, p, art_rect):
        p.save()
        p.setClipRect(art_rect)
        if not self.art.isNull():
            p.drawPixmap(art_rect, pixel.fit(self.art, int(art_rect.width()),
                                             int(art_rect.height()), self.focus,
                                             self.hfocus),
                         QRectF(0, 0, art_rect.width(), art_rect.height()))
        # Knock the busy street back so the subject sprite reads, then tint
        # toward the category colour.
        p.fillRect(art_rect, QColor(7, 10, 17, 172))
        tint = QColor(self.tint)
        tint.setAlpha(52)
        p.fillRect(art_rect, tint)

        if not self.sprite.isNull():
            side = 68 if self._lift else 62
            scaled = self.sprite.scaled(side, side, Qt.KeepAspectRatio,
                                        Qt.FastTransformation)
            p.drawPixmap(int(art_rect.center().x() - scaled.width() / 2),
                         int(art_rect.center().y() - scaled.height() / 2 - 4), scaled)

        fade = QLinearGradient(0, art_rect.bottom() - 40, 0, art_rect.bottom())
        fade.setColorAt(0.0, QColor(15, 20, 31, 0))
        fade.setColorAt(1.0, QColor(theme.SURFACE))
        p.fillRect(art_rect, fade)
        p.restore()

        if self._lift:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, int(14 * self._lift)))
            p.drawRect(art_rect)

    def _paint_body(self, p, rect):
        x = rect.left() + 14
        width = int(rect.width() - 28)
        date_baseline = rect.bottom() - 14
        y = rect.top() + ART_H + 20

        p.setFont(QFont("Noto Sans", 8, QFont.Bold))
        p.setPen(QColor(self.tint))
        p.drawText(int(x), int(y), self.item["category"].upper())

        title_font = QFont("Noto Sans", 10, QFont.DemiBold)
        p.setPen(QColor(theme.TEXT))
        y = self._draw_wrapped(p, title_font, self.item["title"],
                               x, y + 20, width, 2, 17) + 17

        # Whatever is left over goes to the excerpt, never onto the date.
        body_font = QFont("Noto Sans", 9)
        room = int((date_baseline - 10 - y) // 14)
        if room > 0:
            p.setPen(QColor(theme.TEXT_FAINT))
            self._draw_wrapped(p, body_font, self.item["body"],
                               x, y + 12, width, min(room, 3), 14)

        p.setFont(QFont("Noto Sans", 8))
        p.setPen(QColor(theme.TEXT_FAINT))
        p.drawText(int(x), int(date_baseline), self.item["date"])

        if self.item.get("pinned"):
            dot = QRectF(rect.right() - 22, rect.top() + ART_H + 13, 6, 6)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(self.accent))
            p.drawEllipse(dot)

    @staticmethod
    def _draw_wrapped(p, font, text, x, y, width, max_lines, line_height):
        """Draw at most `max_lines` of text, eliding the last one.

        Returns the baseline of the final line drawn.
        """
        p.setFont(font)
        fm = QFontMetrics(font)
        words = text.split()
        lines, line, leftover = [], "", False
        for index, word in enumerate(words):
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
    """Lays the cards out in rows, filtered by category."""

    article_opened = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._filter = "All"
        self._game = None
        self._art = None
        self._cards = []
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
        columns = max(1, (self.width() + GAP) // (CARD_W + GAP))
        for index, card in enumerate(self._cards):
            row, column = divmod(index, columns)
            card.move(column * (CARD_W + GAP), row * (CARD_H + GAP))
        rows = (len(self._cards) + columns - 1) // columns
        self.setMinimumHeight(rows * (CARD_H + GAP) - GAP)

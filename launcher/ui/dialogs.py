"""Modal dialogs: sign in, and reading a notice."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QHBoxLayout

from qfluentwidgets import (MessageBoxBase, SubtitleLabel, BodyLabel, CaptionLabel,
                            LineEdit, PasswordLineEdit, CheckBox, HyperlinkButton,
                            setFont)

from ..core import pixel, theme
from ..core.paths import tile


class LoginDialog(MessageBoxBase):
    def __init__(self, parent=None, remembered: str = ""):
        super().__init__(parent)
        self.title = SubtitleLabel("Sign in to play")

        art = QLabel()
        art.setPixmap(pixel.load(tile("torii"), 1).scaled(
            48, 48, Qt.KeepAspectRatio, Qt.FastTransformation))

        header = QHBoxLayout()
        header.setSpacing(12)
        header.addWidget(art, 0, Qt.AlignVCenter)
        header.addWidget(self.title, 1, Qt.AlignVCenter)

        self.account = LineEdit()
        self.account.setPlaceholderText("Account ID")
        self.account.setText(remembered)
        self.account.setClearButtonEnabled(True)

        self.password = PasswordLineEdit()
        self.password.setPlaceholderText("Password")

        self.remember = CheckBox("Remember my ID")
        self.remember.setChecked(bool(remembered))

        hint = CaptionLabel("This demo does not send your details anywhere.")
        hint.setStyleSheet(f"color: {theme.TEXT_FAINT};")

        links = QHBoxLayout()
        links.addWidget(self.remember)
        links.addStretch(1)
        links.addWidget(HyperlinkButton(
            "https://pyqt-fluent-widgets.readthedocs.io/en/latest/", "Need help?"))

        self.viewLayout.setSpacing(14)
        self.viewLayout.addLayout(header)
        self.viewLayout.addWidget(self.account)
        self.viewLayout.addWidget(self.password)
        self.viewLayout.addLayout(links)
        self.viewLayout.addWidget(hint)

        self.yesButton.setText("SIGN IN")
        self.cancelButton.setText("PLAY AS GUEST")
        self.widget.setMinimumWidth(400)

        self.account.textChanged.connect(self._validate)
        self._validate()

    def _validate(self):
        self.yesButton.setEnabled(bool(self.account.text().strip()))

    @property
    def account_name(self) -> str:
        return self.account.text().strip()


class ArticleDialog(MessageBoxBase):
    def __init__(self, article: dict, parent=None):
        super().__init__(parent)

        category = CaptionLabel(f"{article['category'].upper()}   -   {article['date']}")
        category.setStyleSheet(f"color: {theme.ORANGE}; letter-spacing: 1px;")
        setFont(category, 11, QFont.Bold)

        title = SubtitleLabel(article["title"])
        title.setWordWrap(True)

        body = BodyLabel(article["body"])
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {theme.TEXT_DIM};")

        self.viewLayout.setSpacing(12)
        self.viewLayout.addWidget(category)
        self.viewLayout.addWidget(title)
        self.viewLayout.addWidget(body)

        self.yesButton.setText("Got it")
        self.cancelButton.setVisible(False)
        self.widget.setMinimumWidth(460)

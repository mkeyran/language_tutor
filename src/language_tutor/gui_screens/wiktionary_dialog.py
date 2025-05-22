"""Wiktionary lookup dialog."""

import urllib.parse
from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QShortcut,
    QSizePolicy,
)
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView


class WiktionaryDialog(QDialog):
    """Dialog for searching words on Wiktionary."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wiktionary Lookup")
        self.resize(1200, 900)

        self._setup_ui()

    def _setup_ui(self):
        layout = QGridLayout(self)

        layout.addWidget(QLabel("Word:"), 0, 0)
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter a word")
        layout.addWidget(self.word_input, 0, 1, 1, 2)
        self.word_input.setFocus()

        buttons_layout = QHBoxLayout()
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self._on_search)
        buttons_layout.addWidget(self.search_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._on_clear)
        buttons_layout.addWidget(self.clear_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_btn)

        layout.addLayout(buttons_layout, 1, 0, 1, 3)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view, 2, 0, 1, 3)
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.search_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.search_shortcut.activated.connect(self._on_search)

    def showEvent(self, event):
        super().showEvent(event)
        self.word_input.setFocus()

    def _on_clear(self):
        self.word_input.clear()
        self.web_view.setHtml("")

    def _on_search(self):
        word = self.word_input.text().strip()
        if not word:
            return
        url = "https://en.m.wiktionary.org/wiki/" + urllib.parse.quote(word)
        self.web_view.load(QUrl(url))

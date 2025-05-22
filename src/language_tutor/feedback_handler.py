from PyQt5.QtGui import QFont, QTextDocument, QTextCursor, QColor


class FeedbackHandler:
    """Handle interactive feedback highlighting between mistakes and text."""

    def __init__(self, writing_input, mistakes_display, style_display):
        """Initialize with the text widgets to connect."""
        self.writing_input = writing_input
        self.mistakes_display = mistakes_display
        self.style_display = style_display

        self.grammar_errors = []
        self.style_errors = []
        self.original_text = ""
        self.current_highlighted_error = None
        self._pre_highlight_html = None
        self._pre_highlight_cursor = 0
        self._pre_highlight_scroll = 0

        self.original_stylesheet = self.writing_input.styleSheet()

        self.grammar_highlight_style = """
        .grammar-error {
            background-color: rgba(255, 200, 200, 0.5);
        }
        """
        self.style_highlight_style = """
        .style-error {
            background-color: rgba(200, 200, 255, 0.5);
        }
        """

        self.mistakes_display.mouseMoveEvent = self._create_hover_handler(
            self.mistakes_display, "grammar"
        )
        self.mistakes_display.leaveEvent = self._create_leave_handler()

        self.style_display.mouseMoveEvent = self._create_hover_handler(
            self.style_display, "style"
        )
        self.style_display.leaveEvent = self._create_leave_handler()

    def update_errors(self, grammar_errors, style_errors, text):
        """Update stored errors and text from the last check."""
        self.grammar_errors = grammar_errors
        self.style_errors = style_errors
        self.original_text = text
        self.restore_original_text()

    def _create_hover_handler(self, widget, error_type):
        def hover_handler(event):
            cursor = widget.cursorForPosition(event.pos())
            cursor.select(QTextCursor.BlockUnderCursor)
            line = cursor.selectedText()

            if hasattr(widget.__class__, "mouseMoveEvent"):
                widget.__class__.mouseMoveEvent(widget, event)

            errors = (
                self.grammar_errors if error_type == "grammar" else self.style_errors
            )
            for error_text, _ in errors:
                if error_text and error_text in line:
                    self.highlight_error(error_text, error_type)
                    return

            if self.current_highlighted_error:
                self.restore_original_text()

        return hover_handler

    def _create_leave_handler(self):
        def leave_handler(event):
            if hasattr(self.mistakes_display.__class__, "leaveEvent"):
                self.mistakes_display.__class__.leaveEvent(self.mistakes_display, event)
            self.restore_original_text()

        return leave_handler

    def highlight_error(self, error_text, error_type):
        if not error_text:
            return

        if self.current_highlighted_error:
            self.restore_original_text()

        self.current_highlighted_error = (error_text, error_type)
        self._pre_highlight_scroll = self.writing_input.verticalScrollBar().value()
        self._pre_highlight_cursor = self.writing_input.textCursor().position()
        self._pre_highlight_html = self.writing_input.toHtml()

        bg_color = "#ffcccc" if error_type == "grammar" else "#ccccff"
        processed_text = self._find_and_highlight_error(
            original_text=self._pre_highlight_html,
            error_text=error_text,
            bg_color=bg_color,
        )

        if processed_text == self._pre_highlight_html:
            self.current_highlighted_error = None
            return

        self.writing_input.setHtml(processed_text)
        cursor = self.writing_input.textCursor()
        cursor.setPosition(min(self._pre_highlight_cursor, len(self.writing_input.toPlainText())))
        self.writing_input.setTextCursor(cursor)
        self.writing_input.verticalScrollBar().setValue(self._pre_highlight_scroll)

    def _find_and_highlight_error(self, original_text, error_text, bg_color):
        doc = QTextDocument()
        doc.setHtml(original_text)
        search_error = " ".join(error_text.split())
        search_options = QTextDocument.FindCaseSensitively
        cursor = QTextCursor(doc)
        cursor = doc.find(search_error, cursor, search_options)
        if cursor.isNull():
            import re

            cursor = QTextCursor(doc)
            relaxed_error = r"\b" + r"\b\s+\b".join(search_error.split()) + r"\b"
            pattern = re.compile(relaxed_error, re.IGNORECASE)
            text = doc.toPlainText()
            match = pattern.search(text)
            if match:
                cursor = QTextCursor(doc)
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), QTextCursor.KeepAnchor)
        if not cursor.isNull():
            fmt = cursor.charFormat()
            fmt.setBackground(QColor(bg_color))
            cursor.setCharFormat(fmt)
            return doc.toHtml()
        return original_text

    def restore_original_text(self):
        if not self.current_highlighted_error or self._pre_highlight_html is None:
            return

        self.writing_input.setHtml(self._pre_highlight_html)
        cursor = self.writing_input.textCursor()
        cursor.setPosition(min(self._pre_highlight_cursor, len(self.writing_input.toPlainText())))
        self.writing_input.setTextCursor(cursor)
        self.writing_input.verticalScrollBar().setValue(self._pre_highlight_scroll)

        self.current_highlighted_error = None
        self._pre_highlight_html = None


def format_mistakes_with_hover(mistakes, mistakes_type):
    """Format mistakes with hover functionality."""
    if not mistakes:
        return "No mistakes found."
    doc = QTextDocument()
    cursor = QTextCursor(doc)
    font = QFont("Arial", 12)
    doc.setDefaultFont(font)
    css = """
    <style>
        .grammar-error {
            background-color: rgba(255, 200, 200, 0.5);
        }
        .style-error {
            background-color: rgba(200, 200, 255, 0.5);
        }
    </style>
    """
    cursor.insertHtml(css)

    for error_text, explanation in mistakes:
        if error_text:
            class_name = (
                "grammar-error" if mistakes_type == "grammar" else "style-error"
            )
            formatted_error = f'<span class="{class_name}">{error_text}</span>'
            cursor.insertHtml(f"<div> - {formatted_error}: {explanation}</div><br>")
    return doc.toHtml()

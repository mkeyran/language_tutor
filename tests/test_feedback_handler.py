"""Tests for feedback handler functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt5.QtWidgets import QApplication, QTextEdit

from language_tutor.feedback_handler import FeedbackHandler, format_mistakes_with_hover


@pytest.fixture
def qt_app():
    """Fixture to ensure QApplication exists for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def text_widgets(qt_app):
    """Fixture providing text widgets for testing."""
    writing_input = QTextEdit()
    mistakes_display = QTextEdit()
    style_display = QTextEdit()
    return writing_input, mistakes_display, style_display


@pytest.fixture
def feedback_handler(text_widgets):
    """Fixture providing a FeedbackHandler instance."""
    writing_input, mistakes_display, style_display = text_widgets
    return FeedbackHandler(writing_input, mistakes_display, style_display)


class TestFeedbackHandlerInitialization:
    """Tests for FeedbackHandler initialization."""

    def test_feedback_handler_initialization(self, feedback_handler, text_widgets):
        """Test basic initialization of FeedbackHandler."""
        writing_input, mistakes_display, style_display = text_widgets
        assert feedback_handler.writing_input is writing_input
        assert feedback_handler.mistakes_display is mistakes_display
        assert feedback_handler.style_display is style_display
        assert feedback_handler.grammar_errors == []
        assert feedback_handler.style_errors == []
        assert feedback_handler.original_text == ""

    def test_highlight_styles_initialization(self, feedback_handler):
        """Test that highlight styles are properly initialized."""
        assert hasattr(feedback_handler, "grammar_highlight_style")
        assert hasattr(feedback_handler, "style_highlight_style")
        assert "background-color" in feedback_handler.grammar_highlight_style
        assert "background-color" in feedback_handler.style_highlight_style

    def test_mouse_event_handlers_installation(self, feedback_handler, text_widgets):
        """Test that mouse event handlers are installed."""
        writing_input, mistakes_display, style_display = text_widgets

        # Check that mouse event handlers were installed
        assert hasattr(mistakes_display, "mouseMoveEvent")
        assert hasattr(mistakes_display, "leaveEvent")
        assert hasattr(style_display, "mouseMoveEvent")
        assert hasattr(style_display, "leaveEvent")


class TestErrorUpdating:
    """Tests for error updating functionality."""

    def test_update_errors_empty_lists(self, feedback_handler):
        """Test updating with empty error lists."""
        feedback_handler.update_errors([], [], "")

        # Should not crash and should clear any existing highlights
        assert feedback_handler.grammar_errors == []
        assert feedback_handler.style_errors == []
        assert feedback_handler.original_text == ""

    def test_update_grammar_errors(self, feedback_handler):
        """Test updating grammar errors."""
        text = "I goes to school every day."
        grammar_errors = [("I goes", "Subject-verb disagreement")]

        feedback_handler.update_errors(grammar_errors, [], text)

        # Check that errors were stored
        assert len(feedback_handler.grammar_errors) == 1
        assert feedback_handler.grammar_errors[0][0] == "I goes"
        assert feedback_handler.grammar_errors[0][1] == "Subject-verb disagreement"
        assert feedback_handler.original_text == text

    def test_update_style_errors(self, feedback_handler):
        """Test updating style errors."""
        text = "The book is very very good."
        style_errors = [("very very", "Repetitive use of 'very'")]

        feedback_handler.update_errors([], style_errors, text)

        # Check that errors were stored
        assert len(feedback_handler.style_errors) == 1
        assert feedback_handler.style_errors[0][0] == "very very"
        assert feedback_handler.style_errors[0][1] == "Repetitive use of 'very'"
        assert feedback_handler.original_text == text

    def test_update_mixed_errors(self, feedback_handler):
        """Test updating both grammar and style errors."""
        text = "I goes very very fast."
        grammar_errors = [("I goes", "Subject-verb disagreement")]
        style_errors = [("very very", "Repetitive use")]

        feedback_handler.update_errors(grammar_errors, style_errors, text)

        assert len(feedback_handler.grammar_errors) == 1
        assert len(feedback_handler.style_errors) == 1
        assert feedback_handler.original_text == text


class TestFeedbackHandlerIntegration:
    """Integration tests for FeedbackHandler functionality."""

    def test_complete_feedback_workflow(self, feedback_handler):
        """Test complete workflow from updating errors to displaying them."""
        # Define text and errors
        text_content = "I goes to the store very very quickly yesterday."
        grammar_errors = [
            ("I goes", "Use 'I go' for present tense"),
            ("yesterday", "Inconsistent tense usage"),
        ]
        style_errors = [("very very", "Avoid repetitive adverbs")]

        # Update errors
        feedback_handler.update_errors(grammar_errors, style_errors, text_content)

        # Verify errors are stored
        assert len(feedback_handler.grammar_errors) == 2
        assert len(feedback_handler.style_errors) == 1
        assert feedback_handler.original_text == text_content

        # Verify error content
        grammar_texts = [error[0] for error in feedback_handler.grammar_errors]
        assert "I goes" in grammar_texts
        assert "yesterday" in grammar_texts

        style_texts = [error[0] for error in feedback_handler.style_errors]
        assert "very very" in style_texts

    def test_error_persistence_across_operations(self, feedback_handler):
        """Test that errors persist correctly across operations."""
        text = "I goes to school."
        
        # Add initial errors
        grammar_errors = [("I goes", "Grammar error")]
        feedback_handler.update_errors(grammar_errors, [], text)

        # Verify errors exist
        assert len(feedback_handler.grammar_errors) == 1
        assert feedback_handler.original_text == text

        # Update with new errors (simulates new feedback cycle)
        new_errors = [("She go", "Different error")]
        new_text = "She go to work."
        feedback_handler.update_errors(new_errors, [], new_text)
        
        # Should have new errors
        assert len(feedback_handler.grammar_errors) == 1
        assert feedback_handler.grammar_errors[0][1] == "Different error"
        assert feedback_handler.original_text == new_text

    def test_multiple_feedback_cycles(self, feedback_handler):
        """Test multiple cycles of feedback application."""
        # First cycle
        feedback_handler.update_errors([("I goes", "Error1")], [], "I goes to school.")
        assert len(feedback_handler.grammar_errors) == 1
        assert feedback_handler.grammar_errors[0][1] == "Error1"

        # Second cycle - update with new errors
        feedback_handler.update_errors([("She go", "Error2")], [], "She go to work.")
        assert len(feedback_handler.grammar_errors) == 1
        assert feedback_handler.grammar_errors[0][1] == "Error2"
        assert feedback_handler.original_text == "She go to work."

        # Third cycle - mixed errors
        feedback_handler.update_errors(
            [("They goes", "Grammar")], 
            [("very very", "Style")],
            "They goes very very fast."
        )
        assert len(feedback_handler.grammar_errors) == 1
        assert len(feedback_handler.style_errors) == 1
        assert feedback_handler.original_text == "They goes very very fast."

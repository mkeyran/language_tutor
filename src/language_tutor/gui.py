#!/usr/bin/env python3
"""GUI entry point for Language Tutor application."""

import sys
import os
import nest_asyncio

from PyQt6.QtWidgets import QApplication
from language_tutor.gui_app import LanguageTutorGUI
from language_tutor.languages import exercise_types, definitions
from language_tutor import __version__


def main():
    """Main entry point for the language-tutor-gui command."""
    app = QApplication(sys.argv)
    app.setApplicationName("Language Tutor")
    app.setApplicationVersion(__version__)
    
    # Initialize the main window with exercise types and definitions
    window = LanguageTutorGUI(
        exercise_types=exercise_types,
        exercise_definitions=definitions
    )
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())

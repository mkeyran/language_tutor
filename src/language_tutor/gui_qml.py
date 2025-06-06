"""QtQuick/QML-based GUI for Language Tutor application."""

import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import qmlRegisterType, QQmlApplicationEngine
from PyQt6.QtCore import QUrl

from language_tutor.app_controller import AppController, register_qml_types
from language_tutor.languages import get_language_data


def main():
    """Main entry point for the QtQuick application."""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Language Tutor")
    app.setOrganizationName("Language Tutor")
    
    # Register QML types
    register_qml_types()
    
    # Load language data
    exercise_types, exercise_definitions = get_language_data()
    
    # Create the application controller
    app_controller = AppController(exercise_types, exercise_definitions)
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Register the app controller as a context property
    engine.rootContext().setContextProperty("appController", app_controller)
    
    # Load the main QML file
    qml_file = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    # Check if QML loaded successfully
    if not engine.rootObjects():
        print("Failed to load QML file")
        return -1
    
    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
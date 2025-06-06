"""Tests for the QML application initialization."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl

from language_tutor.app_controller import AppController
from language_tutor.llm import create_provider
from language_tutor.llms.base import LLM


@pytest.fixture(scope="session")
def qt_app():
    """Session-scoped fixture to ensure QApplication exists for tests."""
    import os
    # Set headless mode for CI environments
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def exercise_data():
    """Sample exercise data for testing."""
    exercise_types = {
        "en": [("Essay", "Essay"), ("Letter", "Letter")],
        "pl": [("Esej", "Esej"), ("List", "List")]
    }
    exercise_definitions = {
        "en": {
            "Essay": {
                "expected_length": [100, 200],
                "requirements": "Write a structured essay"
            }
        },
        "pl": {
            "Esej": {
                "expected_length": [80, 150],
                "requirements": "Napisz strukturalny esej"
            }
        }
    }
    return exercise_types, exercise_definitions


class TestQMLApp:
    """Tests for QML application components."""
    
    def test_qml_file_exists(self):
        """Test that the main QML file exists."""
        qml_file = Path(__file__).parent.parent / "src" / "language_tutor" / "qml" / "main.qml"
        assert qml_file.exists(), f"QML file not found at {qml_file}"
    
    def test_dialog_qml_files_exist(self):
        """Test that dialog QML files exist."""
        dialogs_dir = Path(__file__).parent.parent / "src" / "language_tutor" / "qml" / "dialogs"
        
        qa_dialog = dialogs_dir / "QADialog.qml"
        settings_dialog = dialogs_dir / "SettingsDialog.qml"
        wiktionary_dialog = dialogs_dir / "WiktionaryDialog.qml"
        
        assert qa_dialog.exists(), f"QADialog.qml not found at {qa_dialog}"
        assert settings_dialog.exists(), f"SettingsDialog.qml not found at {settings_dialog}"
        assert wiktionary_dialog.exists(), f"WiktionaryDialog.qml not found at {wiktionary_dialog}"
    
    def test_qml_engine_creation(self, qt_app, exercise_data):
        """Test that QML engine can be created and configured."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        # Create app controller
        app_controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Create QML engine
        engine = QQmlApplicationEngine()
        
        # Register context property
        engine.rootContext().setContextProperty("appController", app_controller)
        
        # Verify the context property was set
        assert engine.rootContext().contextProperty("appController") == app_controller
    
    def test_qml_basic_syntax(self):
        """Test that main QML file has basic valid syntax."""
        qml_file = Path(__file__).parent.parent / "src" / "language_tutor" / "qml" / "main.qml"
        
        with open(qml_file, 'r') as f:
            content = f.read()
        
        # Basic syntax checks
        assert "ApplicationWindow" in content
        assert "SplitView" in content
        assert "MenuBar" in content
        assert "appController" in content
        
        # Check for proper QML structure
        assert content.count("{") == content.count("}")  # Balanced braces
        assert "import QtQuick" in content
        assert "import QtQuick.Controls" in content
    
    def test_dialog_qml_basic_syntax(self):
        """Test that dialog QML files have basic valid syntax."""
        dialogs_dir = Path(__file__).parent.parent / "src" / "language_tutor" / "qml" / "dialogs"
        
        for dialog_file in ["QADialog.qml", "SettingsDialog.qml", "WiktionaryDialog.qml"]:
            qml_path = dialogs_dir / dialog_file
            
            with open(qml_path, 'r') as f:
                content = f.read()
            
            # Basic syntax checks
            assert "Popup" in content
            assert "appController" in content
            assert content.count("{") == content.count("}")  # Balanced braces
            assert "import QtQuick" in content
    
    @patch('language_tutor.app_controller.get_config_path')
    def test_app_controller_context_integration(self, mock_config_path, qt_app, exercise_data):
        """Test that AppController integrates properly as QML context."""
        # Mock config path to avoid loading real config
        mock_config_path.return_value = "/nonexistent/path.json"
        
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        app_controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Test that controller has required properties for QML
        assert hasattr(app_controller, 'selectedLanguage')
        assert hasattr(app_controller, 'selectedLevel')
        assert hasattr(app_controller, 'selectedExerciseType')
        assert hasattr(app_controller, 'generateButtonText')
        assert hasattr(app_controller, 'generateButtonEnabled')
        assert hasattr(app_controller, 'wordCountText')
        
        # Test that controller has required methods for QML
        assert hasattr(app_controller, 'setLanguage')
        assert hasattr(app_controller, 'setLevel')
        assert hasattr(app_controller, 'setExerciseType')
        assert hasattr(app_controller, 'generateExercise')
        assert hasattr(app_controller, 'checkWriting')
        
        # Test that models are available
        assert hasattr(app_controller, 'languageModel')
        assert hasattr(app_controller, 'levelModel')
        assert hasattr(app_controller, 'exerciseTypeModel')


class TestQMLIntegration:
    """Integration tests for QML and Python backend."""
    
    @patch('language_tutor.app_controller.get_config_path')
    def test_qml_property_binding_simulation(self, mock_config_path, qt_app, exercise_data):
        """Test simulated QML property binding behavior."""
        # Mock config path
        mock_config_path.return_value = "/nonexistent/path.json"
        
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        app_controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Simulate QML property changes
        app_controller.setLanguage("en")
        assert app_controller.selectedLanguage == "en"
        
        app_controller.setLevel("B1")
        assert app_controller.selectedLevel == "B1"
        
        app_controller.setExerciseType("Essay")
        assert app_controller.selectedExerciseType == "Essay"
        assert app_controller.generateButtonText == "Generate Exercise"
        
        # Test custom exercise mode
        app_controller.setExerciseType("Custom")
        assert app_controller.generateButtonText == "Generate Hints"
        assert app_controller.isCustomExercise == True
    
    @patch('language_tutor.app_controller.get_config_path')
    def test_model_data_access(self, mock_config_path, qt_app, exercise_data):
        """Test that QML models provide correct data access."""
        # Mock config path
        mock_config_path.return_value = "/nonexistent/path.json"
        
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        app_controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Test language model
        lang_model = app_controller.languageModel
        assert lang_model.rowCount() > 0
        
        # Test level model
        level_model = app_controller.levelModel
        assert level_model.rowCount() > 0
        
        # Test exercise type model (should be empty initially)
        exercise_model = app_controller.exerciseTypeModel
        # Initially empty because no language is selected
        
        # Set language and check exercise model updates
        app_controller.setLanguage("en")
        assert exercise_model.rowCount() > 0  # Should now have exercises
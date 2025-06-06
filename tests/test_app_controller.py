"""Tests for the QML AppController."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from PyQt6.QtCore import QCoreApplication

from language_tutor.app_controller import AppController, SimpleListModel
from language_tutor.llm import create_provider
from language_tutor.llms.base import LLM


@pytest.fixture(scope="session")
def qt_app():
    """Session-scoped fixture to ensure QCoreApplication exists for tests."""
    import os
    # Set headless mode for CI environments
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
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


class TestSimpleListModel:
    """Tests for the SimpleListModel."""
    
    def test_initialization_empty(self, qt_app):
        """Test model initialization with empty data."""
        model = SimpleListModel()
        assert model.rowCount() == 0
    
    def test_initialization_with_data(self, qt_app):
        """Test model initialization with data."""
        data = [("English", "en"), ("Polish", "pl")]
        model = SimpleListModel(data)
        assert model.rowCount() == 2
    
    def test_data_retrieval(self, qt_app):
        """Test data retrieval from model."""
        data = [("English", "en"), ("Polish", "pl")]
        model = SimpleListModel(data)
        
        # Test first item
        index = model.index(0, 0)
        assert model.data(index, model.NameRole) == "English"
        assert model.data(index, model.CodeRole) == "en"
        
        # Test second item
        index = model.index(1, 0)
        assert model.data(index, model.NameRole) == "Polish"
        assert model.data(index, model.CodeRole) == "pl"
    
    def test_role_names(self, qt_app):
        """Test role names mapping."""
        model = SimpleListModel()
        roles = model.roleNames()
        assert b'name' in roles.values()
        assert b'code' in roles.values()
    
    def test_set_data(self, qt_app):
        """Test updating model data."""
        model = SimpleListModel([("Old", "old")])
        assert model.rowCount() == 1
        
        new_data = [("New1", "new1"), ("New2", "new2")]
        model.setData(new_data)
        assert model.rowCount() == 2
        
        index = model.index(0, 0)
        assert model.data(index, model.NameRole) == "New1"


class TestAppController:
    """Tests for the AppController class."""
    
    def test_initialization(self, qt_app, exercise_data):
        """Test AppController initialization."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        assert controller.exercise_types_all == exercise_types
        assert controller.exercise_definitions_all == exercise_definitions
        assert controller.llm_provider == llm_provider
        assert controller.state is not None
    
    @patch('language_tutor.app_controller.get_config_path')
    def test_property_getters(self, mock_config_path, qt_app, exercise_data):
        """Test property getters."""
        # Mock config path to return non-existent file
        mock_config_path.return_value = "/nonexistent/path.json"
        
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Test initial values (should be empty since config doesn't exist)
        assert controller.selectedLanguage == ""
        assert controller.selectedLevel == ""
        assert controller.selectedExerciseType == ""
        assert controller.generatedExercise == ""
        assert controller.writingInput == ""
        assert controller.generateButtonText == "Generate Exercise"
        assert controller.generateButtonEnabled == True
    
    def test_set_language(self, qt_app, exercise_data):
        """Test setting language."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Test language change
        controller.setLanguage("en")
        assert controller.selectedLanguage == "en"
        assert len(controller.exercise_types) == 2  # Should reload definitions
    
    def test_set_exercise_type_custom(self, qt_app, exercise_data):
        """Test setting custom exercise type."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        controller.setExerciseType("Custom")
        assert controller.selectedExerciseType == "Custom"
        assert controller.generateButtonText == "Generate Hints"
        assert controller.isCustomExercise == True
    
    def test_set_exercise_type_normal(self, qt_app, exercise_data):
        """Test setting normal exercise type."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        controller.setExerciseType("Essay")
        assert controller.selectedExerciseType == "Essay"
        assert controller.generateButtonText == "Generate Exercise"
        assert controller.isCustomExercise == False
    
    def test_set_writing_input(self, qt_app, exercise_data):
        """Test setting writing input."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        test_text = "This is a test writing sample."
        controller.setWritingInput(test_text)
        assert controller.writingInput == test_text
    
    def test_word_count_update(self, qt_app, exercise_data):
        """Test word count updating."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Set language and exercise type first
        controller.setLanguage("en")
        controller.setExerciseType("Essay")
        
        # Set writing with word count within range (100-200 words expected)
        words = " ".join(["word"] * 150)  # 150 words
        controller.setWritingInput(words)
        
        assert "150" in controller.wordCountText
        assert controller.wordCountColor == "#000000"  # Should be black (valid)
        
        # Test with too few words
        short_text = "Too short"
        controller.setWritingInput(short_text)
        assert controller.wordCountColor == "#ff0000"  # Should be red (invalid)
    
    @patch('language_tutor.app_controller.run_async')
    def test_generate_exercise_call(self, mock_run_async, qt_app, exercise_data):
        """Test generate exercise method call."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        controller.generateExercise()
        mock_run_async.assert_called_once()
    
    @patch('language_tutor.app_controller.run_async')
    def test_check_writing_call(self, mock_run_async, qt_app, exercise_data):
        """Test check writing method call."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        controller.checkWriting()
        mock_run_async.assert_called_once()
    
    def test_status_message_updates(self, qt_app, exercise_data):
        """Test status message updating."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        test_message = "Test status message"
        controller.setStatusMessage(test_message)
        assert controller.statusMessage == test_message
    
    def test_button_state_management(self, qt_app, exercise_data):
        """Test button state management."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Test generate button
        controller.setGenerateButtonEnabled(False)
        controller.setGenerateButtonText("Loading...")
        assert controller.generateButtonEnabled == False
        assert controller.generateButtonText == "Loading..."
        
        # Test check button
        controller.setCheckButtonEnabled(False)
        controller.setCheckButtonText("Checking...")
        assert controller.checkButtonEnabled == False
        assert controller.checkButtonText == "Checking..."


class TestAppControllerIntegration:
    """Integration tests for AppController with real-like scenarios."""
    
    def test_complete_workflow_simulation(self, qt_app, exercise_data):
        """Test a complete workflow simulation."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Simulate user selecting options
        controller.setLanguage("en")
        controller.setLevel("B1")
        controller.setExerciseType("Essay")
        
        # Verify state
        assert controller.selectedLanguage == "en"
        assert controller.selectedLevel == "B1"
        assert controller.selectedExerciseType == "Essay"
        assert controller.isCustomExercise == False
        
        # Simulate entering writing
        controller.setWritingInput("This is a sample essay text for testing purposes.")
        assert len(controller.writingInput) > 0
        
        # Word count should update
        assert "10" in controller.wordCountText  # Should show word count
    
    def test_custom_exercise_workflow(self, qt_app, exercise_data):
        """Test custom exercise workflow."""
        exercise_types, exercise_definitions = exercise_data
        mock_llm = Mock(spec=LLM)
        mock_llm.is_configured.return_value = True
        llm_provider = create_provider(mock_llm)
        
        controller = AppController(exercise_types, exercise_definitions, llm_provider)
        
        # Set to custom exercise
        controller.setExerciseType("Custom")
        assert controller.generateButtonText == "Generate Hints"
        assert controller.isCustomExercise == True
        
        # Set custom exercise text
        custom_exercise = "Write about your favorite hobby"
        controller.setCustomExercise(custom_exercise)
        assert controller.generatedExercise == custom_exercise
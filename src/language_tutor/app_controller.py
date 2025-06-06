"""Main application controller for QtQuick/QML interface."""

import os
import json
import random
import datetime
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, QAbstractListModel, QModelIndex, Qt, pyqtSlot
from PyQt6.QtQml import qmlRegisterType
from dotenv import load_dotenv

from language_tutor.llm import create_provider, LLMProvider
from language_tutor.config import (
    LANGUAGES,
    LEVELS,
    get_config_path,
    get_state_path,
    get_export_path,
    get_config_dir,
    DEFAULT_TEXT_FONT_SIZE,
)
from language_tutor.exercise import (
    generate_exercise,
    generate_custom_hints,
    check_writing,
)
from language_tutor.async_runner import run_async
from language_tutor.state import LanguageTutorState
from language_tutor.feedback_handler import format_mistakes_with_hover


class SimpleListModel(QAbstractListModel):
    """Simple list model for combo boxes."""
    
    NameRole = Qt.ItemDataRole.UserRole + 1
    CodeRole = Qt.ItemDataRole.UserRole + 2
    
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._data):
            return None
            
        item = self._data[index.row()]
        if role == self.NameRole:
            return item[0]
        elif role == self.CodeRole:
            return item[1]
        elif role == Qt.ItemDataRole.DisplayRole:
            return item[0]
        return None
    
    def roleNames(self):
        return {
            self.NameRole: b'name',
            self.CodeRole: b'code'
        }
    
    def setData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()


class AppController(QObject):
    """Main application controller bridging QML and Python backend."""
    
    # Signals for property changes
    languageChanged = pyqtSignal(str)
    levelChanged = pyqtSignal(str)
    exerciseTypeChanged = pyqtSignal(str)
    generatedExerciseChanged = pyqtSignal(str)
    generatedHintsChanged = pyqtSignal(str)
    writingInputChanged = pyqtSignal(str)
    writingMistakesChanged = pyqtSignal(str)
    styleErrorsChanged = pyqtSignal(str)
    recommendationsChanged = pyqtSignal(str)
    statusMessageChanged = pyqtSignal(str)
    generateButtonTextChanged = pyqtSignal(str)
    generateButtonEnabledChanged = pyqtSignal(bool)
    checkButtonTextChanged = pyqtSignal(str)
    checkButtonEnabledChanged = pyqtSignal(bool)
    wordCountTextChanged = pyqtSignal(str)
    wordCountColorChanged = pyqtSignal(str)
    isCustomExerciseChanged = pyqtSignal(bool)
    
    def __init__(self, exercise_types, exercise_definitions, llm_provider: LLMProvider | None = None):
        super().__init__()
        
        self.exercise_types_all = exercise_types
        self.exercise_definitions_all = exercise_definitions
        self.exercise_definitions = {}
        self.exercise_types = []
        
        # Initialize LLM provider
        self.llm_provider = llm_provider or create_provider()
        
        # Centralize application state
        self.state = LanguageTutorState()
        
        # File sync helpers
        self.file_sync_enabled = False
        self.file_sync_path = ""
        
        # UI state
        self._status_message = ""
        self._generate_button_text = "Generate Exercise"
        self._generate_button_enabled = True
        self._check_button_text = "Check Writing"
        self._check_button_enabled = True
        self._word_count_text = "Word Count: 0"
        self._word_count_color = "#000000"
        self._is_custom_exercise = False
        
        # Create models for QML combo boxes
        self.language_model = SimpleListModel(LANGUAGES)
        self.level_model = SimpleListModel(LEVELS)
        self.exercise_type_model = SimpleListModel([])
        
        # Load configuration
        self._load_config()
        
        # Configure LLM
        env_path = os.path.join(get_config_dir(), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        llm = self.llm_provider.get_llm()
        llm.set_api_key(os.getenv("OPENROUTER_API_KEY", ""))
        llm.set_base_url("https://openrouter.ai/api/v1")
        
        # Check for API key
        if not llm.is_configured():
            self.setStatusMessage("Error: API Key not configured. Please configure it in Settings.")
    
    # Property getters and setters
    @pyqtProperty(str, notify=languageChanged)
    def selectedLanguage(self):
        return self.state.selected_language
    
    @pyqtProperty(str, notify=levelChanged)
    def selectedLevel(self):
        return self.state.selected_level
    
    @pyqtProperty(str, notify=exerciseTypeChanged)
    def selectedExerciseType(self):
        return self.state.selected_exercise
    
    @pyqtProperty(str, notify=generatedExerciseChanged)
    def generatedExercise(self):
        return self.state.generated_exercise
    
    @pyqtProperty(str, notify=generatedHintsChanged)
    def generatedHints(self):
        return self.state.generated_hints
    
    @pyqtProperty(str, notify=writingInputChanged)
    def writingInput(self):
        return self.state.writing_input
    
    @pyqtProperty(str, notify=writingMistakesChanged)
    def writingMistakes(self):
        return self.state.writing_mistakes
    
    @pyqtProperty(str, notify=styleErrorsChanged)
    def styleErrors(self):
        return self.state.style_errors
    
    @pyqtProperty(str, notify=recommendationsChanged)
    def recommendations(self):
        return self.state.recommendations
    
    @pyqtProperty(str, notify=statusMessageChanged)
    def statusMessage(self):
        return self._status_message
    
    @pyqtProperty(str, notify=generateButtonTextChanged)
    def generateButtonText(self):
        return self._generate_button_text
    
    @pyqtProperty(bool, notify=generateButtonEnabledChanged)
    def generateButtonEnabled(self):
        return self._generate_button_enabled
    
    @pyqtProperty(str, notify=checkButtonTextChanged)
    def checkButtonText(self):
        return self._check_button_text
    
    @pyqtProperty(bool, notify=checkButtonEnabledChanged)
    def checkButtonEnabled(self):
        return self._check_button_enabled
    
    @pyqtProperty(str, notify=wordCountTextChanged)
    def wordCountText(self):
        return self._word_count_text
    
    @pyqtProperty(str, notify=wordCountColorChanged)
    def wordCountColor(self):
        return self._word_count_color
    
    @pyqtProperty(bool, notify=isCustomExerciseChanged)
    def isCustomExercise(self):
        return self._is_custom_exercise
    
    @pyqtProperty(QObject, constant=True)
    def languageModel(self):
        return self.language_model
    
    @pyqtProperty(QObject, constant=True)
    def levelModel(self):
        return self.level_model
    
    @pyqtProperty(QObject, constant=True)
    def exerciseTypeModel(self):
        return self.exercise_type_model
    
    def setStatusMessage(self, message):
        if self._status_message != message:
            self._status_message = message
            self.statusMessageChanged.emit(message)
    
    def setGenerateButtonText(self, text):
        if self._generate_button_text != text:
            self._generate_button_text = text
            self.generateButtonTextChanged.emit(text)
    
    def setGenerateButtonEnabled(self, enabled):
        if self._generate_button_enabled != enabled:
            self._generate_button_enabled = enabled
            self.generateButtonEnabledChanged.emit(enabled)
    
    def setCheckButtonText(self, text):
        if self._check_button_text != text:
            self._check_button_text = text
            self.checkButtonTextChanged.emit(text)
    
    def setCheckButtonEnabled(self, enabled):
        if self._check_button_enabled != enabled:
            self._check_button_enabled = enabled
            self.checkButtonEnabledChanged.emit(enabled)
    
    def setWordCountText(self, text):
        if self._word_count_text != text:
            self._word_count_text = text
            self.wordCountTextChanged.emit(text)
    
    def setWordCountColor(self, color):
        if self._word_count_color != color:
            self._word_count_color = color
            self.wordCountColorChanged.emit(color)
    
    def setIsCustomExercise(self, is_custom):
        if self._is_custom_exercise != is_custom:
            self._is_custom_exercise = is_custom
            self.isCustomExerciseChanged.emit(is_custom)
    
    # Slot methods for QML
    @pyqtSlot(str)
    def setLanguage(self, language_code: str):
        """Set the selected language."""
        if self.state.selected_language != language_code:
            self.state.selected_language = language_code
            self.languageChanged.emit(language_code)
            self._reload_definitions()
            self._save_config()
            # Find language name for display
            lang_name = next((name for name, code in LANGUAGES if code == language_code), language_code)
            self.setStatusMessage(f"Language set to: {lang_name}")
    
    @pyqtSlot(str)
    def setLevel(self, level_code: str):
        """Set the selected level."""
        if self.state.selected_level != level_code:
            self.state.selected_level = level_code
            self.levelChanged.emit(level_code)
            self._save_config()
            # Find level name for display
            level_name = next((name for name, code in LEVELS if code == level_code), level_code)
            self.setStatusMessage(f"Level set to: {level_name}")
    
    @pyqtSlot(str)
    def setExerciseType(self, exercise_type: str):
        """Set the selected exercise type."""
        if self.state.selected_exercise != exercise_type:
            self.state.selected_exercise = exercise_type
            self.exerciseTypeChanged.emit(exercise_type)
            
            if exercise_type == "Custom":
                self.setGenerateButtonText("Generate Hints")
                self.setIsCustomExercise(True)
                self.setStatusMessage("Custom exercise selected. Edit the task above.")
            else:
                self.setGenerateButtonText("Generate Exercise")
                self.setIsCustomExercise(False)
                self.setStatusMessage(f"Exercise type set to: {exercise_type}")
            
            self._update_word_count()
    
    @pyqtSlot(str)
    def setWritingInput(self, text: str):
        """Set the writing input text."""
        if self.state.writing_input != text:
            self.state.writing_input = text
            self.writingInputChanged.emit(text)
            self._update_word_count()
    
    @pyqtSlot(str)
    def setCustomExercise(self, text: str):
        """Set custom exercise text."""
        if self.state.generated_exercise != text:
            self.state.generated_exercise = text
            self.generatedExerciseChanged.emit(text)
    
    @pyqtSlot()
    def generateExercise(self):
        """Generate a new exercise."""
        run_async(self._generate_exercise())
    
    @pyqtSlot()
    def checkWriting(self):
        """Check the user's writing."""
        run_async(self._check_writing())
    
    @pyqtSlot()
    def saveState(self):
        """Save the current application state."""
        try:
            self.state.save(get_state_path())
            self.setStatusMessage("State saved successfully.")
        except Exception as e:
            self.setStatusMessage(f"Error saving state: {str(e)}")
    
    @pyqtSlot()
    def loadState(self):
        """Load the application state."""
        try:
            if os.path.exists(get_state_path()):
                state = LanguageTutorState.load(get_state_path())
                self.state = state
                self._restore_ui_from_state()
                self.setStatusMessage("State loaded successfully.")
            else:
                self.setStatusMessage("No saved state found.")
        except Exception as e:
            self.setStatusMessage(f"Error loading state: {str(e)}")
    
    @pyqtSlot()
    def exportMarkdown(self):
        """Export the current session to Markdown."""
        try:
            md = self.state.to_markdown()
            
            datetime_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            export_dir = get_export_path()
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            safe_filename = f"{self.state.selected_language}_{self.state.selected_exercise}_{datetime_str}.md".replace(
                " ", "_"
            ).replace("/", "_")
            file_path = os.path.join(export_dir, safe_filename)
            
            with open(file_path, "w") as f:
                f.write(md)
            self.setStatusMessage(f"Exported to {file_path}")
        except Exception as e:
            self.setStatusMessage(f"Error exporting Markdown: {str(e)}")
    
    # Private methods
    def _load_config(self):
        """Load configuration from config file."""
        env_path = os.path.join(get_config_dir(), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        if os.path.exists(get_config_path()):
            try:
                with open(get_config_path(), "r") as f:
                    config = json.load(f)
                
                self.state.selected_language = config.get("selected_language", "")
                self.state.selected_level = config.get("selected_level", "")
                self.file_sync_enabled = config.get("file_sync_enabled", False)
                self.file_sync_path = config.get("file_sync_path", "")
                
                self._reload_definitions()
                
                self.setStatusMessage(
                    f"Loaded config: Language={self.state.selected_language}, Level={self.state.selected_level}"
                )
            except Exception as e:
                self.setStatusMessage(f"Error loading config: {str(e)}")
    
    def _save_config(self):
        """Save configuration to config file."""
        config = {}
        if os.path.exists(get_config_path()):
            try:
                with open(get_config_path(), "r") as f:
                    config = json.load(f)
            except Exception:
                pass
        
        config.update({
            "selected_language": self.state.selected_language,
            "selected_level": self.state.selected_level,
            "file_sync_enabled": self.file_sync_enabled,
            "file_sync_path": self.file_sync_path,
        })
        
        try:
            with open(get_config_path(), "w") as f:
                json.dump(config, f)
        except Exception as e:
            self.setStatusMessage(f"Error saving config: {str(e)}")
    
    def _reload_definitions(self):
        """Reload exercise definitions based on selected language."""
        self.exercise_types = self.exercise_types_all.get(self.state.selected_language, [])
        self.exercise_definitions = self.exercise_definitions_all.get(
            self.state.selected_language, {}
        )
        
        # Update the exercise type model
        self.exercise_type_model.setData(self.exercise_types)
    
    def _update_word_count(self):
        """Update the word count display."""
        word_count = len(self.state.writing_input.split()) if self.state.writing_input else 0
        
        if (
            not self.state.selected_exercise
            or self.state.selected_exercise not in self.exercise_definitions
        ):
            self.setWordCountText(f"Word Count: {word_count}")
            self.setWordCountColor("#000000")
        else:
            min_words = self.exercise_definitions[self.state.selected_exercise]["expected_length"][0]
            max_words = self.exercise_definitions[self.state.selected_exercise]["expected_length"][1]
            
            self.setWordCountText(f"Word Count: {word_count}, min {min_words}, max {max_words}")
            
            if word_count < min_words or word_count > max_words:
                self.setWordCountColor("#ff0000")
            else:
                self.setWordCountColor("#000000")
    
    def _restore_ui_from_state(self):
        """Restore UI state from loaded state."""
        # Emit all change signals to update QML
        self.languageChanged.emit(self.state.selected_language)
        self.levelChanged.emit(self.state.selected_level)
        self.exerciseTypeChanged.emit(self.state.selected_exercise)
        self.generatedExerciseChanged.emit(self.state.generated_exercise)
        self.generatedHintsChanged.emit(self.state.generated_hints)
        self.writingInputChanged.emit(self.state.writing_input)
        self.writingMistakesChanged.emit(self.state.writing_mistakes)
        self.styleErrorsChanged.emit(self.state.style_errors)
        self.recommendationsChanged.emit(self.state.recommendations)
        
        # Update button states
        if self.state.selected_exercise == "Custom":
            self.setGenerateButtonText("Generate Hints")
            self.setIsCustomExercise(True)
        else:
            self.setGenerateButtonText("Generate Exercise")
            self.setIsCustomExercise(False)
        
        self._update_word_count()
    
    async def _generate_exercise(self):
        """Generate a new exercise."""
        if self.state.selected_exercise == "Custom":
            custom_text = self.state.generated_exercise.strip()
            if not custom_text:
                self.setStatusMessage("Enter your custom exercise in the text box above.")
                return
            
            llm = self.llm_provider.get_llm()
            if not llm.is_configured():
                self.setStatusMessage("API Key not configured. Please set your OpenRouter API key in Settings.")
                return
            
            self.setGenerateButtonEnabled(False)
            self.setGenerateButtonText("Generating...")
            self.setStatusMessage("Generating hints for custom exercise...")
            
            try:
                hints, cost = await generate_custom_hints(
                    language=self.state.selected_language,
                    level=self.state.selected_level,
                    exercise_text=custom_text,
                    llm_provider=self.llm_provider,
                )
                
                self.state.generated_hints = hints
                self.generatedHintsChanged.emit(hints)
                self.setStatusMessage(f"Hints generated! Cost: {cost:.4f} USD")
            except Exception as e:
                self.setStatusMessage(f"Error generating hints: {str(e)}")
                self.state.generated_hints = f"Error: {str(e)}"
                self.generatedHintsChanged.emit(self.state.generated_hints)
            finally:
                self.setGenerateButtonEnabled(True)
                self.setGenerateButtonText("Generate Hints")
            return
        
        if not self.state.selected_language or not self.state.selected_exercise:
            self.setStatusMessage("Please select both a language and an exercise type.")
            return
        
        llm = self.llm_provider.get_llm()
        if not llm.is_configured():
            self.setStatusMessage("API Key not configured. Please set your OpenRouter API key in Settings.")
            return
        
        # Show loading state
        self.setGenerateButtonEnabled(False)
        self.setGenerateButtonText("Generating...")
        self.setStatusMessage(
            f"Generating '{self.state.selected_exercise}' exercise for {self.state.selected_language}..."
        )
        
        try:
            # Use utility function to generate exercise
            exercise_text, hints, cost = await generate_exercise(
                language=self.state.selected_language,
                level=self.state.selected_level,
                exercise_type=self.state.selected_exercise,
                definitions=self.exercise_definitions,
                llm_provider=self.llm_provider,
            )
            
            # Update stored values
            self.state.generated_exercise = exercise_text
            self.state.generated_hints = hints
            
            # Emit signals to update QML
            self.generatedExerciseChanged.emit(exercise_text)
            self.generatedHintsChanged.emit(hints)
            self.setStatusMessage(f"Exercise generated! Cost: {cost:.4f} USD")
            
        except Exception as e:
            self.setStatusMessage(f"Error generating exercise: {str(e)}")
            self.state.generated_exercise = f"Error: {str(e)}"
            self.generatedExerciseChanged.emit(self.state.generated_exercise)
        finally:
            # Reset button state
            self.setGenerateButtonEnabled(True)
            self.setGenerateButtonText("Generate Exercise")
    
    async def _check_writing(self):
        """Check the user's writing."""
        if self.state.selected_exercise == "Custom":
            self.state.generated_exercise = self.state.generated_exercise
        
        if not self.state.generated_exercise or not self.state.writing_input:
            self.setStatusMessage("Please generate an exercise and write something first.")
            return
        
        llm = self.llm_provider.get_llm()
        if not llm.is_configured():
            self.setStatusMessage("API Key not configured. Please set your OpenRouter API key in Settings.")
            return
        
        # Show loading state
        self.setCheckButtonEnabled(False)
        self.setCheckButtonText("Checking...")
        self.setStatusMessage("Checking your writing...")
        
        try:
            # Use utility function to check writing
            mistakes, style_errors, recommendations, cost = await check_writing(
                language=self.state.selected_language,
                level=self.state.selected_level,
                exercise_text=self.state.generated_exercise,
                writing_input=self.state.writing_input,
                exercise_type=self.state.selected_exercise,
                definitions=self.exercise_definitions,
                llm_provider=self.llm_provider,
            )
            
            # Store raw feedback for state restoration
            self.state.grammar_errors_raw = mistakes
            self.state.style_errors_raw = style_errors
            
            # Update stored values with formatted content
            self.state.writing_mistakes = format_mistakes_with_hover(mistakes, "grammar")
            self.state.style_errors = format_mistakes_with_hover(style_errors, "style")
            self.state.recommendations = recommendations
            
            # Emit signals to update QML
            self.writingMistakesChanged.emit(self.state.writing_mistakes)
            self.styleErrorsChanged.emit(self.state.style_errors)
            self.recommendationsChanged.emit(self.state.recommendations)
            
            self.setStatusMessage(f"Feedback provided! Cost: {cost:.4f} USD")
            
        except Exception as e:
            self.setStatusMessage(f"Error checking writing: {str(e)}")
            self.state.writing_mistakes = f"Error: {str(e)}"
            self.writingMistakesChanged.emit(self.state.writing_mistakes)
        finally:
            # Reset button state
            self.setCheckButtonEnabled(True)
            self.setCheckButtonText("Check Writing")


# Register the types for QML
def register_qml_types():
    """Register custom types for use in QML."""
    qmlRegisterType(AppController, "LanguageTutor", 1, 0, "AppController")
    qmlRegisterType(SimpleListModel, "LanguageTutor", 1, 0, "SimpleListModel")
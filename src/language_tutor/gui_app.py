"""Main GUI Application for Language Tutor."""

import os
import json
import random
import datetime
import litellm
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton, QTextEdit, 
    QSplitter, QApplication, QMessageBox, QAction,
    QFileDialog, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextDocument

from language_tutor.config import (
    LANGUAGES, LEVELS, 
    get_config_path, get_state_path, get_export_path, get_config_dir
)
from language_tutor.utils import generate_exercise, check_writing
from language_tutor.gui_screens import QADialog, SettingsDialog


class LanguageTutorGUI(QMainWindow):
    """PyQt GUI for Language Tutor application."""
    
    def __init__(self, exercise_types, exercise_definitions):
        """Initialize the GUI with exercise types and definitions."""
        super().__init__()
        
        self.exercise_types_all = exercise_types
        self.exercise_definitions_all = exercise_definitions
        self.exercise_definitions = {}
        self.exercise_types = []
        
        # Initialize state variables
        self.selected_language = ""
        self.selected_exercise = ""
        self.selected_level = ""
        self.generated_exercise = ""
        self.generated_hints = ""
        self.writing_mistakes = ""
        self.style_errors = ""
        self.recommendations = ""
        self.writing_input = ""
        
        # Set up the UI
        self.setWindowTitle("Language Tutor")
        self.resize(1000, 700)
        
        self._setup_ui()
        self._setup_menu()
        self._load_config()
        
        # Configure LiteLLM
        env_path = os.path.join(get_config_dir(), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        litellm.api_key = os.getenv("OPENROUTER_API_KEY")
        litellm.base_url = "https://openrouter.ai/api/v1"
        
        # Check for API key
        if not litellm.api_key:
            self.statusBar().showMessage(
                "Error: API Key not configured. Please configure it in Settings.",
                10000
            )
    
    def _setup_ui(self):
        """Set up the main UI components."""
        # Create main splitter with left and right panes
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # Left pane - Exercise generation
        self.left_pane = QWidget()
        self.left_layout = QVBoxLayout(self.left_pane)
        
        # Language selection
        self.left_layout.addWidget(QLabel("Language:"))
        self.language_select = QComboBox()
        for name, code in LANGUAGES:
            self.language_select.addItem(name, code)
        self.language_select.currentIndexChanged.connect(self._on_language_changed)
        self.left_layout.addWidget(self.language_select)
        
        # Level selection
        self.left_layout.addWidget(QLabel("Level:"))
        self.level_select = QComboBox()
        for name, code in LEVELS:
            self.level_select.addItem(name, code)
        self.level_select.currentIndexChanged.connect(self._on_level_changed)
        self.left_layout.addWidget(self.level_select)
        
        # Exercise type selection
        self.left_layout.addWidget(QLabel("Exercise Type:"))
        self.exercise_select = QComboBox()
        self.exercise_select.currentIndexChanged.connect(self._on_exercise_changed)
        self.left_layout.addWidget(self.exercise_select)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Exercise")
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        self.left_layout.addWidget(self.generate_btn)
        
        # Exercise display
        self.left_layout.addWidget(QLabel("Exercise:"))
        self.exercise_display = QTextEdit()
        self.exercise_display.setReadOnly(True)
        self.left_layout.addWidget(self.exercise_display)
        
        # Hints display
        self.left_layout.addWidget(QLabel("Hints:"))
        self.hints_display = QTextEdit()
        self.hints_display.setReadOnly(True)
        self.left_layout.addWidget(self.hints_display)
        
        # Right pane - Writing check
        self.right_pane = QWidget()
        self.right_layout = QVBoxLayout(self.right_pane)
        
        # Writing input
        self.right_layout.addWidget(QLabel("Your Writing:"))
        self.writing_input_area = QTextEdit()
        self.writing_input_area.textChanged.connect(self._on_writing_changed)
        self.right_layout.addWidget(self.writing_input_area)
        
        # Word count
        self.word_count_label = QLabel("Word Count: 0")
        self.right_layout.addWidget(self.word_count_label)
        
        # Check button
        self.check_btn = QPushButton("Check Writing")
        self.check_btn.clicked.connect(self._on_check_clicked)
        self.right_layout.addWidget(self.check_btn)
        
        # Feedback sections
        self.right_layout.addWidget(QLabel("Mistakes:"))
        self.mistakes_display = QTextEdit()
        self.mistakes_display.setReadOnly(True)
        self.right_layout.addWidget(self.mistakes_display)
        
        self.right_layout.addWidget(QLabel("Stylistic Errors:"))
        self.style_display = QTextEdit()
        self.style_display.setReadOnly(True)
        self.right_layout.addWidget(self.style_display)
        
        self.right_layout.addWidget(QLabel("Recommendations:"))
        self.recs_display = QTextEdit()
        self.recs_display.setReadOnly(True)
        self.right_layout.addWidget(self.recs_display)
        
        # Add panes to splitter
        self.main_splitter.addWidget(self.left_pane)
        self.main_splitter.addWidget(self.right_pane)
        self.main_splitter.setSizes([400, 600])
        
        # Create status bar
        self.statusBar()
    
    def _setup_menu(self):
        """Set up the application menu."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        save_action = QAction("&Save State", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_state)
        file_menu.addAction(save_action)
        
        load_action = QAction("&Load State", self)
        load_action.setShortcut("Ctrl+L")
        load_action.triggered.connect(self.load_state)
        file_menu.addAction(load_action)
        
        export_action = QAction("&Export Markdown", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_markdown)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        qa_action = QAction("&Ask AI", self)
        qa_action.setShortcut("Ctrl+A")
        qa_action.triggered.connect(self.open_qa_dialog)
        tools_menu.addAction(qa_action)
        
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings_dialog)
        tools_menu.addAction(settings_action)
    
    def _load_config(self):
        """Load configuration from config file."""
        env_path = os.path.join(get_config_dir(), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            
        if os.path.exists(get_config_path()):
            try:
                with open(get_config_path(), "r") as f:
                    config = json.load(f)
                
                # Set language and level from config
                lang = config.get("selected_language", "")
                level = config.get("selected_level", "")
                
                if lang:
                    index = next((i for i, item in enumerate(LANGUAGES) if item[1] == lang), 0)
                    self.language_select.setCurrentIndex(index)
                
                if level:
                    index = next((i for i, item in enumerate(LEVELS) if item[1] == level), 0)
                    self.level_select.setCurrentIndex(index)
                    
                self.statusBar().showMessage(
                    f"Loaded config: Language={lang}, Level={level}", 
                    3000
                )
            except Exception as e:
                self.statusBar().showMessage(f"Error loading config: {str(e)}", 5000)
    
    def _save_config(self):
        """Save configuration to config file."""
        config = {
            "selected_language": self.selected_language,
            "selected_level": self.selected_level,
        }
        try:
            with open(get_config_path(), "w") as f:
                json.dump(config, f)
        except Exception as e:
            self.statusBar().showMessage(f"Error saving config: {str(e)}", 5000)
    
    def _on_language_changed(self, index):
        """Handle language selection change."""
        if index >= 0:
            self.selected_language = self.language_select.itemData(index)
            self._reload_definitions()
            self._save_config()
            self.statusBar().showMessage(f"Language set to: {self.language_select.itemText(index)}", 3000)
    
    def _on_level_changed(self, index):
        """Handle level selection change."""
        if index >= 0:
            self.selected_level = self.level_select.itemData(index)
            self._save_config()
            self.statusBar().showMessage(f"Level set to: {self.level_select.itemText(index)}", 3000)
    
    def _on_exercise_changed(self, index):
        """Handle exercise type selection change."""
        if index >= 0:
            exercise_text = self.exercise_select.itemText(index)
            if exercise_text == "Random":
                # Select a random exercise type (skip the first "Random" option)
                if self.exercise_select.count() <= 1:
                    self.statusBar().showMessage("No other exercise types available.", 3000)
                    return
                random_index = random.randint(1, self.exercise_select.count() - 1)
                self.exercise_select.setCurrentIndex(random_index)
                return
            
            self.selected_exercise = exercise_text
            self.statusBar().showMessage(f"Exercise type set to: {exercise_text}", 3000)
            self._update_word_count()
    
    def _reload_definitions(self):
        """Reload exercise definitions based on selected language."""
        self.exercise_types = self.exercise_types_all.get(self.selected_language, [])
        self.exercise_definitions = self.exercise_definitions_all.get(self.selected_language, {})
        
        # Update the exercise select options
        self.exercise_select.clear()
        for exercise_type in self.exercise_types:
            self.exercise_select.addItem(exercise_type[0], exercise_type[1])
    
    def _on_writing_changed(self):
        """Handle changes in the writing input."""
        self.writing_input = self.writing_input_area.toPlainText()
        self._update_word_count()
    
    def _update_word_count(self):
        """Update the word count label."""
        word_count = len(self.writing_input_area.toPlainText().split())
        
        if (not self.selected_exercise or 
            self.selected_exercise not in self.exercise_definitions):
            self.word_count_label.setText(f"Word Count: {word_count}")
        else:
            min_words = self.exercise_definitions[self.selected_exercise]['expected_length'][0]
            max_words = self.exercise_definitions[self.selected_exercise]['expected_length'][1]
            
            self.word_count_label.setText(
                f"Word Count: {word_count}, min {min_words}, max {max_words}"
            )
            
            if word_count < min_words or word_count > max_words:
                self.word_count_label.setStyleSheet("color: red;")
            else:
                self.word_count_label.setStyleSheet("")
    
    async def _generate_exercise(self):
        """Generate a new exercise."""
        if not self.selected_language or not self.selected_exercise:
            QMessageBox.warning(
                self, 
                "Missing Selection", 
                "Please select both a language and an exercise type."
            )
            return
            
        if not litellm.api_key:
            QMessageBox.critical(
                self,
                "API Key Required",
                "API Key not configured. Please set your OpenRouter API key in Settings."
            )
            return
        
        # Show loading state
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Generating...")
        self.exercise_display.setText("Generating...")
        self.hints_display.setText("")  # Clear previous hints
        
        self.statusBar().showMessage(
            f"Generating '{self.selected_exercise}' exercise for {self.selected_language}...",
            5000
        )
        
        try:
            # Use utility function to generate exercise
            exercise_text, hints, cost = await generate_exercise(
                language=self.selected_language,
                level=self.selected_level,
                exercise_type=self.selected_exercise,
                definitions=self.exercise_definitions,
            )
            
            # Update stored values
            self.generated_exercise = exercise_text
            self.generated_hints = hints
            
            # Update TextEdits
            self.exercise_display.setText(self.generated_exercise)
            self.hints_display.setText(self.generated_hints)
            self.statusBar().showMessage(f"Exercise generated! Cost: {cost:.4f} USD", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error Generating Exercise", str(e))
            self.exercise_display.setText(f"Error: {str(e)}")
        finally:
            # Reset button state
            self.generate_btn.setEnabled(True)
            self.generate_btn.setText("Generate Exercise")
    
    async def _check_writing(self):
        """Check the user's writing."""
        self.writing_input = self.writing_input_area.toPlainText()
        
        if not self.generated_exercise or not self.writing_input:
            QMessageBox.warning(
                self,
                "Missing Content",
                "Please generate an exercise and write something first."
            )
            return
            
        if not litellm.api_key:
            QMessageBox.critical(
                self,
                "API Key Required",
                "API Key not configured. Please set your OpenRouter API key in Settings."
            )
            return
        
        # Show loading state
        self.check_btn.setEnabled(False)
        self.check_btn.setText("Checking...")
        self.mistakes_display.setText("Checking...")
        self.style_display.setText("")
        self.recs_display.setText("")
        
        self.statusBar().showMessage("Checking your writing...", 5000)
        
        try:
            # Use utility function to check writing
            mistakes, style_errors, recommendations, cost = await check_writing(
                language=self.selected_language,
                level=self.selected_level,
                exercise_text=self.generated_exercise,
                writing_input=self.writing_input,
                exercise_type=self.selected_exercise,
                definitions=self.exercise_definitions,
            )
            
            # Update stored values and displays
            self.writing_mistakes = mistakes
            self.style_errors = style_errors
            self.recommendations = recommendations
            
            self.mistakes_display.setText(self.writing_mistakes)
            self.style_display.setText(self.style_errors)
            self.recs_display.setText(self.recommendations)
            
            self.statusBar().showMessage(f"Feedback provided! Cost: {cost:.4f} USD", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error Checking Writing", str(e))
            self.mistakes_display.setText(f"Error: {str(e)}")
        finally:
            # Reset button state
            self.check_btn.setEnabled(True)
            self.check_btn.setText("Check Writing")
    
    def _run_async(self, coro):
        """Run an async coroutine from a synchronous method.
        
        Args:
            coro: The coroutine to run
        """
        import asyncio
        import nest_asyncio
        
        # Apply nest_asyncio to allow nested event loops (needed in some environments)
        try:
            nest_asyncio.apply()
        except RuntimeError:
            # If already applied or not needed, continue
            pass
        
        # Get or create an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the coroutine
        return loop.run_until_complete(coro)
    
    def _on_generate_clicked(self):
        """Handle generate button click."""
        self._run_async(self._generate_exercise())
    
    def _on_check_clicked(self):
        """Handle check button click."""
        self._run_async(self._check_writing())
    
    def save_state(self):
        """Save the current application state."""
        try:
            state = {
                "selected_language": self.selected_language,
                "selected_exercise": self.selected_exercise,
                "selected_level": self.selected_level,
                "generated_exercise": self.generated_exercise,
                "generated_hints": self.generated_hints,
                "writing_input": self.writing_input,
                "mistakes": self.writing_mistakes,
                "style": self.style_errors,
                "recs": self.recommendations,
            }
            with open(get_state_path(), "w") as f:
                json.dump(state, f)
            self.statusBar().showMessage("State saved successfully.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error Saving State", str(e))
    
    def load_state(self):
        """Load the application state."""
        if not os.path.exists(get_state_path()):
            self.statusBar().showMessage("No saved state found.", 3000)
            return
            
        try:
            with open(get_state_path(), "r") as f:
                state = json.load(f)
            
            # Restore language first (this will reload definitions)
            lang = state.get("selected_language", "")
            if lang:
                index = next((i for i, item in enumerate(LANGUAGES) if item[1] == lang), -1)
                if index >= 0:
                    self.language_select.setCurrentIndex(index)
            
            # Restore level
            level = state.get("selected_level", "")
            if level:
                index = next((i for i, item in enumerate(LEVELS) if item[1] == level), -1)
                if index >= 0:
                    self.level_select.setCurrentIndex(index)
            
            # Restore exercise type
            exercise = state.get("selected_exercise", "")
            if exercise:
                index = self.exercise_select.findText(exercise)
                if index >= 0:
                    self.exercise_select.setCurrentIndex(index)
            
            # Restore content
            self.generated_exercise = state.get("generated_exercise", "")
            self.generated_hints = state.get("generated_hints", "")
            self.writing_input = state.get("writing_input", "")
            self.writing_mistakes = state.get("mistakes", "")
            self.style_errors = state.get("style", "")
            self.recommendations = state.get("recs", "")
            
            # Update UI
            self.exercise_display.setText(self.generated_exercise)
            self.hints_display.setText(self.generated_hints)
            self.writing_input_area.setText(self.writing_input)
            self.mistakes_display.setText(self.writing_mistakes)
            self.style_display.setText(self.style_errors)
            self.recs_display.setText(self.recommendations)
            
            self.statusBar().showMessage("State loaded successfully.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading State", str(e))
    
    def export_markdown(self):
        """Export the current exercise, writing, and feedback to a Markdown file."""
        try:
            exercise = self.generated_exercise or ""
            hints = self.generated_hints or ""
            writing = self.writing_input or ""
            mistakes = self.writing_mistakes or ""
            style = self.style_errors or ""
            recs = self.recommendations or ""
            
            md = f"""# Language Tutor Export

**Language:** {self.selected_language}
**Level:** {self.selected_level}
**Exercise Type:** {self.selected_exercise}

## Exercise
{exercise}

## Hints
{hints if hints else "None."}

## Your Writing
{writing}

## Mistakes
{mistakes if mistakes else "None."}

## Stylistic Errors
{style if style else "None."}

## Recommendations
{recs if recs else "None."}
"""
            
            datetime_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            export_dir = get_export_path()
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
                
            safe_filename = f"{self.selected_language}_{self.selected_exercise}_{datetime_str}.md".replace(" ", "_").replace("/", "_")
            file_path = os.path.join(export_dir, safe_filename)
            
            # Ask user for confirmation/location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Markdown",
                file_path,
                "Markdown Files (*.md)"
            )
            
            if file_path:
                with open(file_path, "w") as f:
                    f.write(md)
                self.statusBar().showMessage(f"Exported to {file_path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error Exporting Markdown", str(e))
    
    def open_qa_dialog(self):
        """Open the QA dialog."""
        if not self.generated_exercise:
            QMessageBox.warning(self, "No Exercise", "Please generate an exercise first.")
            return
            
        dialog = QADialog(self)
        dialog.set_context({
            "language": self.selected_language,
            "level": self.selected_level,
            "exercise_type": self.selected_exercise,
            "exercise": self.generated_exercise,
        })
        dialog.exec_()
    
    def open_settings_dialog(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        result = dialog.exec_()
        
        if result == SettingsDialog.Accepted:
            # Reload API key
            litellm.api_key = os.getenv("OPENROUTER_API_KEY")
            self.statusBar().showMessage("Settings updated successfully.", 3000)

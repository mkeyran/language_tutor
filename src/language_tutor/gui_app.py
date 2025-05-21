"""Main GUI Application for Language Tutor."""

import os
import json
import random
import datetime
from language_tutor.llm import llm
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton, QTextEdit, 
    QSplitter, QApplication, QMessageBox, QAction,
    QFileDialog, QStatusBar, QTabWidget, QShortcut, QFrame, QFormLayout, QGroupBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextDocument, QKeySequence, QTextCursor, QColor

from language_tutor.config import (
    LANGUAGES, LEVELS, 
    get_config_path, get_state_path, get_export_path, get_config_dir
)
from language_tutor.exercise import generate_exercise, check_writing
from language_tutor.async_runner import run_async
from language_tutor.gui_screens import QADialog, SettingsDialog
from language_tutor.state import LanguageTutorState
from language_tutor.feedback_handler import FeedbackHandler, format_mistakes_with_hover


class LanguageTutorGUI(QMainWindow):
    """PyQt GUI for Language Tutor application."""
    
    def __init__(self, exercise_types, exercise_definitions):
        """Initialize the GUI with exercise types and definitions."""
        super().__init__()
        
        self.exercise_types_all = exercise_types
        self.exercise_definitions_all = exercise_definitions
        self.exercise_definitions = {}
        self.exercise_types = []

        # Centralize application state
        self.state = LanguageTutorState()

        # Convenience aliases to keep code readable
        # Access state fields via properties defined below

        # Set up the UI
        self.setWindowTitle("Language Tutor")
        self.resize(1000, 700)
        
        self._setup_ui()
        self._setup_menu()
        self._load_config()
        
        # Configure LLM
        env_path = os.path.join(get_config_dir(), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        llm.set_api_key(os.getenv("OPENROUTER_API_KEY", ""))
        llm.set_base_url("https://openrouter.ai/api/v1")
        
        # Check for API key
        if not llm.is_configured():
            self.statusBar().showMessage(
                "Error: API Key not configured. Please configure it in Settings.",
                10000
            )

    # --- State property helpers ---
    @property
    def selected_language(self) -> str:
        return self.state.selected_language

    @selected_language.setter
    def selected_language(self, value: str) -> None:
        self.state.selected_language = value

    @property
    def selected_exercise(self) -> str:
        return self.state.selected_exercise

    @selected_exercise.setter
    def selected_exercise(self, value: str) -> None:
        self.state.selected_exercise = value

    @property
    def selected_level(self) -> str:
        return self.state.selected_level

    @selected_level.setter
    def selected_level(self, value: str) -> None:
        self.state.selected_level = value

    @property
    def generated_exercise(self) -> str:
        return self.state.generated_exercise

    @generated_exercise.setter
    def generated_exercise(self, value: str) -> None:
        self.state.generated_exercise = value

    @property
    def generated_hints(self) -> str:
        return self.state.generated_hints

    @generated_hints.setter
    def generated_hints(self, value: str) -> None:
        self.state.generated_hints = value

    @property
    def writing_mistakes(self) -> str:
        return self.state.writing_mistakes

    @writing_mistakes.setter
    def writing_mistakes(self, value: str) -> None:
        self.state.writing_mistakes = value

    @property
    def style_errors(self) -> str:
        return self.state.style_errors

    @style_errors.setter
    def style_errors(self, value: str) -> None:
        self.state.style_errors = value

    @property
    def recommendations(self) -> str:
        return self.state.recommendations

    @recommendations.setter
    def recommendations(self, value: str) -> None:
        self.state.recommendations = value

    @property
    def writing_input(self) -> str:
        return self.state.writing_input

    @writing_input.setter
    def writing_input(self, value: str) -> None:
        self.state.writing_input = value
    
    def _setup_ui(self):
        """Set up the main UI components."""
        # Create main splitter with left and right panes
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # Load default stylesheet for text areas from .styles.css file in the same directory
        stylesheet_path = os.path.join(os.path.dirname(__file__), "styles.css")
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, "r") as f:
                self.text_area_default_stylesheet = f.read()
        else:
            # Fallback to a default stylesheet if the file doesn't exist
            self.text_area_default_stylesheet = """
            QTextEdit {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                font-size: 14px;
                padding: 5px;
            }
            """


        # Left pane - Exercise generation
        self.left_pane = QWidget()
        self.left_layout = QVBoxLayout(self.left_pane)
        
        # Create a frame to group the selection widgets
        self.selection_frame = QGroupBox()
        selection_layout = QFormLayout(self.selection_frame)
        selection_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Language selection
        self.language_select = QComboBox()
        for name, code in LANGUAGES:
            self.language_select.addItem(name, code)
        self.language_select.currentIndexChanged.connect(self._on_language_changed)
        selection_layout.addRow("Language:", self.language_select)

        # Level selection
        self.level_select = QComboBox()
        for name, code in LEVELS:
            self.level_select.addItem(name, code)
        self.level_select.currentIndexChanged.connect(self._on_level_changed)
        selection_layout.addRow("Level:", self.level_select)
        
        # Exercise type selection
        self.exercise_select = QComboBox()
        self.exercise_select.currentIndexChanged.connect(self._on_exercise_changed)
        selection_layout.addRow("Exercise Type:", self.exercise_select)

        # Generate button
        self.generate_btn = QPushButton("Generate Exercise")
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        selection_layout.addRow(self.generate_btn)
        
        # Add the frame to the main layout
        self.left_layout.addWidget(self.selection_frame)
        
        # Create a frame for exercise and hints display
        self.display_frame = QGroupBox()
        display_layout = QVBoxLayout(self.display_frame)
        
        # Exercise display
        display_layout.addWidget(QLabel("Exercise:"))
        self.exercise_display = QTextEdit()
        self.exercise_display.setReadOnly(True)
        display_layout.addWidget(self.exercise_display)
        
        # Hints display
        display_layout.addWidget(QLabel("Hints:"))
        self.hints_display = QTextEdit()
        self.hints_display.setReadOnly(True)
        display_layout.addWidget(self.hints_display)
        
        # Add the display frame to the main layout
        self.left_layout.addWidget(self.display_frame)
        
        # Right pane - Writing check
        self.right_pane = QWidget()
        self.right_layout = QVBoxLayout(self.right_pane)
        
        # Writing input
        self.writing_frame = QGroupBox("")
        
        frame_layout = QVBoxLayout(self.writing_frame)
        self.right_layout.addWidget(self.writing_frame)

        self.writing_input_area = QTextEdit()
        
        self.writing_input_area.setPlaceholderText("Write your text here...")
        self.writing_input_area.textChanged.connect(self._on_writing_changed)
        frame_layout.addWidget(self.writing_input_area)

        # Add Ctrl+Enter shortcut for checking writing
        self.check_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.check_shortcut.activated.connect(self._on_check_clicked)
        
        # Check button
        self.check_btn = QPushButton("Check Writing")
        self.check_btn.clicked.connect(self._on_check_clicked)
        frame_layout.addWidget(self.check_btn)
        
        # Feedback sections in tabbed widget
        self.feedback_frame = QGroupBox("")
        self.right_layout.addWidget(self.feedback_frame)
        feedback_layout = QVBoxLayout(self.feedback_frame)
        self.feedback_tabs = QTabWidget()
        
        # Mistakes tab
        self.mistakes_display = QTextEdit()
        self.mistakes_display.setReadOnly(True)
        self.feedback_tabs.addTab(self.mistakes_display, "Mistakes")
        self.mistakes_display.document().setDefaultStyleSheet(self.text_area_default_stylesheet)
        
        # Stylistic Errors tab
        self.style_display = QTextEdit()
        self.style_display.setReadOnly(True)
        self.feedback_tabs.addTab(self.style_display, "Stylistic Errors")
        self.style_display.document().setDefaultStyleSheet(self.text_area_default_stylesheet)
        # Recommendations tab
        self.recs_display = QTextEdit()
        self.recs_display.setReadOnly(True)
        self.feedback_tabs.addTab(self.recs_display, "Recommendations")
        self.recs_display.document().setDefaultStyleSheet(self.text_area_default_stylesheet)

        feedback_layout.addWidget(self.feedback_tabs)
        
        # Add panes to splitter
        self.main_splitter.addWidget(self.left_pane)
        self.main_splitter.addWidget(self.right_pane)
        self.main_splitter.setSizes([300, 700])
        
        # Create status bar with permanent word count section
        self.statusBar()
        self.word_count_status = QLabel("Word Count: 0")
        self.statusBar().addPermanentWidget(self.word_count_status)
        
        # Initialize the feedback handler
        self.feedback_handler = FeedbackHandler(
            self.writing_input_area, 
            self.mistakes_display, 
            self.style_display
        )
    
    def _setup_menu(self):
        """Set up the application menu."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        save_action = QAction("&Save State", self)
        save_action.setShortcut("Ctrl+Alt+S")
        save_action.triggered.connect(self.save_state)
        file_menu.addAction(save_action)
        
        load_action = QAction("&Load State", self)
        load_action.setShortcut("Ctrl+Alt+L")
        load_action.triggered.connect(self.load_state)
        file_menu.addAction(load_action)
        
        export_action = QAction("&Export Markdown", self)
        export_action.setShortcut("Ctrl+Alt+E")
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
        qa_action.setShortcut("Ctrl+G")
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
        """Update the word count in the status bar."""
        word_count = len(self.writing_input_area.toPlainText().split())
        
        if (not self.selected_exercise or 
            self.selected_exercise not in self.exercise_definitions):
            self.word_count_status.setText(f"Word Count: {word_count}")
        else:
            min_words = self.exercise_definitions[self.selected_exercise]['expected_length'][0]
            max_words = self.exercise_definitions[self.selected_exercise]['expected_length'][1]
            
            self.word_count_status.setText(
                f"Word Count: {word_count}, min {min_words}, max {max_words}"
            )
            
            if word_count < min_words or word_count > max_words:
                self.word_count_status.setStyleSheet("color: red;")
            else:
                self.word_count_status.setStyleSheet("")
    
    async def _generate_exercise(self):
        """Generate a new exercise."""
        if not self.selected_language or not self.selected_exercise:
            QMessageBox.warning(
                self, 
                "Missing Selection", 
                "Please select both a language and an exercise type."
            )
            return
            
        if not llm.is_configured():
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
            
            # Update TextEdits with Markdown
            self.exercise_display.setMarkdown(self.generated_exercise)
            self.hints_display.setMarkdown(self.generated_hints)
            self.statusBar().showMessage(f"Exercise generated! Cost: {cost:.4f} USD", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error Generating Exercise", str(e))
            self.exercise_display.setMarkdown(f"Error: {str(e)}")
        finally:
            # Reset button state
            self.generate_btn.setEnabled(True)
            self.generate_btn.setText("Generate Exercise")
    
    async def _check_writing(self):
        """Check the user's writing."""
        self.writing_input = self.writing_input_area.toMarkdown()
        # Store the HTML representation for interactive feedback recovery
        self.state.writing_input_html = self.writing_input_area.toHtml()

        if not self.generated_exercise or not self.writing_input:
            QMessageBox.warning(
                self,
                "Missing Content",
                "Please generate an exercise and write something first."
            )
            return
            
        if not llm.is_configured():
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
            
            # Store raw feedback for state restoration
            self.state.grammar_errors_raw = mistakes
            self.state.style_errors_raw = style_errors

            # Update stored values and displays with HTML formatted content
            self.writing_mistakes = format_mistakes_with_hover(mistakes, "grammar")
            self.style_errors = format_mistakes_with_hover(style_errors, "style")
            self.recommendations = recommendations
            
            # Use setHtml instead of setMarkdown to support our custom HTML
            self.mistakes_display.setHtml(self.writing_mistakes)
            self.style_display.setHtml(self.style_errors)
            self.recs_display.setMarkdown(self.recommendations)
            
            # Update the feedback handler with the errors
            self.feedback_handler.update_errors(
                self.state.grammar_errors_raw,
                self.state.style_errors_raw,
                self.state.writing_input_html,
            )
            
            self.statusBar().showMessage(f"Feedback provided! Cost: {cost:.4f} USD", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error Checking Writing", str(e))
            self.mistakes_display.setMarkdown(f"Error: {str(e)}")
            raise e
        finally:
            # Reset button state
            self.check_btn.setEnabled(True)
            self.check_btn.setText("Check Writing")
        
    def _on_generate_clicked(self):
        """Handle generate button click."""
        run_async(self._generate_exercise())
    
    def _on_check_clicked(self):
        """Handle check button click."""
        run_async(self._check_writing())
    
    def save_state(self):
        """Save the current application state."""
        try:
            self.state.save()
            self.statusBar().showMessage("State saved successfully.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error Saving State", str(e))
    
    def load_state(self):
        """Load the application state."""
        if not os.path.exists(get_state_path()):
            self.statusBar().showMessage("No saved state found.", 3000)
            return

        try:
            state = LanguageTutorState.load()
            self.state = state
            
            # Restore language first (this will reload definitions)
            lang = state.selected_language
            if lang:
                index = next((i for i, item in enumerate(LANGUAGES) if item[1] == lang), -1)
                if index >= 0:
                    self.language_select.setCurrentIndex(index)

            # Restore level
            level = state.selected_level
            if level:
                index = next((i for i, item in enumerate(LEVELS) if item[1] == level), -1)
                if index >= 0:
                    self.level_select.setCurrentIndex(index)

            # Restore exercise type
            exercise = state.selected_exercise
            if exercise:
                index = self.exercise_select.findText(exercise)
                if index >= 0:
                    self.exercise_select.setCurrentIndex(index)

            # Restore content
            self.generated_exercise = state.generated_exercise
            self.generated_hints = state.generated_hints
            self.writing_input = state.writing_input
            self.writing_mistakes = state.writing_mistakes
            self.style_errors = state.style_errors
            self.recommendations = state.recommendations
            self.state.grammar_errors_raw = state.grammar_errors_raw
            self.state.style_errors_raw = state.style_errors_raw
            self.state.writing_input_html = state.writing_input_html
            
            # Update UI with Markdown
            self.exercise_display.setMarkdown(self.generated_exercise)
            self.hints_display.setMarkdown(self.generated_hints)
            self.writing_input_area.setText(self.writing_input)
            self.mistakes_display.setMarkdown(self.writing_mistakes)
            self.style_display.setMarkdown(self.style_errors)
            self.recs_display.setMarkdown(self.recommendations)

            # Restore interactive feedback connections
            self.feedback_handler.update_errors(
                self.state.grammar_errors_raw,
                self.state.style_errors_raw,
                self.state.writing_input_html,
            )
            
            self.statusBar().showMessage("State loaded successfully.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading State", str(e))
    
    def export_markdown(self):
        """Export the current exercise, writing, and feedback to a Markdown file."""
        try:
            md = self.state.to_markdown()
            
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
            llm.set_api_key(os.getenv("OPENROUTER_API_KEY", ""))
            self.statusBar().showMessage("Settings updated successfully.", 3000)

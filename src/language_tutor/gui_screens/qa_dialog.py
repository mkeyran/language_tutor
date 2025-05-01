"""QA Dialog module for language tutor application."""

import json
import os
import litellm
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, 
    QTextEdit, QPushButton, QHBoxLayout, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

from language_tutor.config import AI_MODELS, get_config_path
from language_tutor.utils import answer_question
from language_tutor.utils import run_async

class QADialog(QDialog):
    """A dialog for asking questions to the AI model."""
    
    def __init__(self, parent=None):
        """Initialize the QA dialog."""
        super().__init__(parent)
        
        self.selected_model = ""
        self.context = {}
        self.last_query = ""
        self.last_response = ""
        self.last_cost = 0.0
        
        self.setWindowTitle("Ask AI Assistant")
        self.resize(600, 500)
        
        self._setup_ui()
        self._load_config()
    
    def set_context(self, context):
        """Set the context dictionary for the QA dialog."""
        self.context = context
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Model selection
        layout.addWidget(QLabel("Select AI Model:"))
        self.model_select = QComboBox()
        for name, model_id in AI_MODELS:
            self.model_select.addItem(name, model_id)
        self.model_select.currentIndexChanged.connect(self._on_model_changed)
        layout.addWidget(self.model_select)
        
        # Question input
        layout.addWidget(QLabel("Your Question:"))
        self.question_input = QTextEdit()
        self.question_input.setFixedHeight(100)
        layout.addWidget(self.question_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._on_send_clicked)
        buttons_layout.addWidget(self.send_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        buttons_layout.addWidget(self.clear_btn)
        layout.addLayout(buttons_layout)
        
        # Answer display
        layout.addWidget(QLabel("Assistant's Answer:"))
        self.answer_display = QTextEdit()
        self.answer_display.setReadOnly(True)
        layout.addWidget(self.answer_display)
        
        # Cost display
        self.cost_display = QLabel("Cost: ")
        layout.addWidget(self.cost_display)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        # Keyboard shortcuts
        self.send_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.send_shortcut.activated.connect(self._on_send_clicked)
        self.clear_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.clear_shortcut.activated.connect(self._on_clear_clicked)
        self.close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_shortcut.activated.connect(self.close)
        self.question_input.setFocus()
        self.question_input.setPlaceholderText("Type your question here...")
        self.answer_display.setPlaceholderText("AI's answer will appear here...")
        self.cost_display.setText("Cost: unknown")
    
    def showEvent(self, event):
        """Override showEvent to set focus to the question input when dialog is shown."""
        super().showEvent(event)
        self.question_input.setFocus()
    
    def _load_config(self):
        """Load the previously selected model from config."""
        try:
            if os.path.exists(get_config_path()):
                with open(get_config_path(), "r") as f:
                    config = json.load(f)
                    model = config.get("qa_model", AI_MODELS[0][1])
                    
                    # Find the index in the combo box
                    for i in range(self.model_select.count()):
                        if self.model_select.itemData(i) == model:
                            self.model_select.setCurrentIndex(i)
                            self.selected_model = model
                            break
        except:
            # If loading fails, set the default model
            self.selected_model = AI_MODELS[0][1]
    
    def _on_model_changed(self, index):
        """Handle model selection changes."""
        if index >= 0:
            self.selected_model = self.model_select.itemData(index)
            
            # Save the selected model to config
            try:
                config_path = get_config_path()
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        config = json.load(f)
                else:
                    config = {}
                
                config["qa_model"] = self.selected_model
                
                with open(config_path, "w") as f:
                    json.dump(config, f)
            except Exception as e:
                print(f"Error saving model selection: {e}")
    
    def _on_clear_clicked(self):
        """Handle clear button click."""
        self.question_input.clear()
        self.answer_display.clear()
        self.cost_display.setText("Cost: ")
    

    async def _send_question(self):
        """Send the question to the AI model."""
        question = self.question_input.toPlainText()
        if not question:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Empty Question", "Please enter a question first.")
            return
        
        if not litellm.api_key:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, 
                "API Key Required",
                "API Key not configured. Cannot send question."
            )
            return
        
        # Show loading state
        self.send_btn.setEnabled(False)
        self.send_btn.setText("Sending...")
        self.answer_display.setMarkdown("Generating answer...")
        
        try:
            # Use utility function to get answer
            answer, cost = await answer_question(
                model=self.selected_model,
                question=question,
                context=self.context
            )
            
            # Update display with Markdown
            self.last_response = answer
            self.answer_display.setMarkdown(answer)
            
            # Update cost display
            if cost:
                self.last_cost = cost
                self.cost_display.setText(f"Cost: ${cost:.6f}")
            else:
                self.cost_display.setText("Cost: unknown")
        
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error querying AI: {str(e)}")
            self.answer_display.setMarkdown(f"Error: {str(e)}")
        
        finally:
            # Reset button state
            self.send_btn.setEnabled(True)
            self.send_btn.setText("Send")
    
    def _on_send_clicked(self):
        """Handle send button click."""
        run_async(self._send_question())

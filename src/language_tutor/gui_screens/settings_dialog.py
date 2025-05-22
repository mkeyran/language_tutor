"""Settings Dialog module for language tutor application."""

import os
import json
from language_tutor.llm import llm
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QSpinBox,
)

from language_tutor.config import (
    get_config_path,
    get_config_dir,
    DEFAULT_TEXT_FONT_SIZE,
)


class SettingsDialog(QDialog):
    """A dialog for configuring application settings."""
    
    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Settings")
        self.resize(400, 150)
        
        self._setup_ui()
        self._load_api_key()
        self._load_font_size()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # API Key input
        layout.addWidget(QLabel("OpenRouter API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your OpenRouter API key")
        layout.addWidget(self.api_key_input)

        # Font size setting
        layout.addWidget(QLabel("Text Font Size (px):"))
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 48)
        self.font_size_input.setValue(DEFAULT_TEXT_FONT_SIZE)
        layout.addWidget(self.font_size_input)
        
        # Status message
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._on_save_clicked)
        buttons_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_api_key(self):
        """Load the API key from the .env file."""
        try:
            env_path = os.path.join(get_config_dir(), ".env")
            
            if os.path.exists(env_path):
                # Read API key from .env file
                with open(env_path, "r") as f:
                    for line in f:
                        if line.startswith("OPENROUTER_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            if api_key:
                                # Set API key in input field
                                self.api_key_input.setText(api_key)
                                break
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def _load_font_size(self):
        """Load text font size from the config file."""
        try:
            if os.path.exists(get_config_path()):
                with open(get_config_path(), "r") as f:
                    config = json.load(f)
                    size = config.get("text_font_size")
                    if isinstance(size, int):
                        self.font_size_input.setValue(size)
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
    
    def _on_save_clicked(self):
        """Handle save button click."""
        api_key = self.api_key_input.text()
        font_size = self.font_size_input.value()
        
        if not api_key:
            QMessageBox.warning(self, "Error", "API key cannot be empty")
            return
        
        try:
            # Ensure config directory exists
            config_dir = get_config_dir()
            env_path = os.path.join(config_dir, ".env")
            
            # Create or update the .env file
            with open(env_path, "w") as f:
                f.write(f"OPENROUTER_API_KEY={api_key}\n")
            
            os.environ["OPENROUTER_API_KEY"] = api_key
            llm.set_api_key(api_key)
            
            # Save font size to config.json
            if os.path.exists(get_config_path()):
                with open(get_config_path(), "r") as f:
                    config = json.load(f)
            else:
                config = {}
            config["text_font_size"] = font_size
            with open(get_config_path(), "w") as f:
                json.dump(config, f)

            self.status_label.setText("Settings saved successfully!")
            self.status_label.setStyleSheet("color: green;")
            
            # Close the dialog after a delay
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1000, self.accept)
            
        except Exception as e:
            self.status_label.setText(f"Error saving API key: {str(e)}")
            self.status_label.setStyleSheet("color: red;")


"""Settings Screen module for language tutor application."""

import json
import os
import litellm

from pathlib import Path
import asyncio
from textual.screen import Screen
from textual.widgets import Button, Static, Input, Footer, Header
from textual.containers import Vertical
from language_tutor.config import get_config_path, get_config_dir


class SettingsScreen(Screen):
    """A modal screen for configuring application settings."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Close Settings"),
    ]

    def compose(self):
        """Create child widgets for the settings screen."""
        yield Header()

        yield Static("OpenRouter API Key:", id="api-key-label", classes="label")
        yield Input(
            id="api-key-input",
            password=True,
            placeholder="Enter your OpenRouter API key",
        )

        with Vertical():
            yield Button("Save", id="save-btn", variant="primary")
            yield Button("Cancel", id="cancel-btn")

        yield Static(id="status-message", classes="status-message")
        yield Footer()

    def on_mount(self):
        """Called when the screen is mounted."""
        # Try to load the API key from .env file or config
        try:
            env_path = os.path.join(get_config_dir(), ".env")

            if os.path.exists(env_path):
                # Read API key from .env file
                with open(env_path, "r") as f:
                    for line in f:
                        if line.startswith("OPENROUTER_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            if api_key:
                                # Show placeholder asterisks instead of the actual key
                                self.query_one("#api-key-input", Input).value = api_key
                                break
        except Exception as e:
            self.query_one("#status-message", Static).update(f"Error: {e}")

    async def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "save-btn":
            await self.save_api_key()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

    async def save_api_key(self):
        """Save the API key to .env file and update app state."""
        api_key = self.query_one("#api-key-input", Input).value
        status = self.query_one("#status-message", Static)

        if not api_key:
            status.update("Error: API key cannot be empty")
            return

        try:
            # Ensure config directory exists
            config_dir = get_config_dir()
            env_path = os.path.join(config_dir, ".env")

            # Create or update the .env file
            with open(env_path, "w") as f:
                f.write(f"OPENROUTER_API_KEY={api_key}\n")

            os.environ["OPENROUTER_API_KEY"] = api_key
            litellm.api_key = api_key

            status.update("API key saved successfully!")

            # Update the status message's appearance
            status.add_class("success")

            # Auto-close after a delay
            await asyncio.sleep(1)
            self.app.pop_screen()

        except Exception as e:
            status.update(f"Error saving API key: {e}")
            status.add_class("error")

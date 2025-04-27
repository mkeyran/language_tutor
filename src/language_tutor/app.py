"""Main application module for Language Tutor."""

import datetime
import json
import os
import importlib.resources as resources
from dotenv import load_dotenv
import litellm
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header,
    Footer,
    Button,
    Select,
    Static,
    TextArea,
    Markdown,
)
from textual.reactive import var

from language_tutor.languages import exercise_types, definitions
from language_tutor.config import (
    LANGUAGES,
    LEVELS,
    get_config_path,
    get_state_path,
    get_export_path,
    get_config_dir,
)
from language_tutor.utils import generate_exercise, check_writing
from language_tutor.screens import QAScreen, SettingsScreen


class LanguageTutorApp(App):
    """A Textual app to help with foreign language writing exercises."""

    def __init__(self, excercise_types, excercise_definitions, *args, **kwargs):
        """Initialize the app with exercise types and definitions."""
        super().__init__(*args, **kwargs)
        self.excercise_types_all = excercise_types
        self.excercise_definitions_all = excercise_definitions
        self.excercise_definitions = {}
        self.excercise_types = []

    BINDINGS = [
        ("ctrl+s", "save_state", "Save"),
        ("ctrl+l", "load_state", "Load"),
        ("ctrl+e", "export_markdown", "Export Markdown"),
        ("ctrl+a", "open_qa_screen", "Ask AI"),
        ("ctrl+underscore", "open_settings", "Settings"),
    ]

    # Use importlib.resources instead of deprecated pkg_resources
    CSS_PATH = resources.files("language_tutor") / "styles.tcss"

    # Reactive variables to store selections and generated content
    selected_language = var("")
    selected_exercise = var("")
    selected_level = var("")
    generated_exercise = var("")
    generated_hints = var("")
    # Adding reactive variables for feedback components
    writing_mistakes = var("")
    style_errors = var("")
    recommendations = var("")
    writing_input = var("")

    def save_config(self):
        """Save selected_language and selected_level to config.json."""
        config = {
            "selected_language": self.selected_language,
            "selected_level": self.selected_level,
        }
        try:
            with open(get_config_path(), "w") as f:
                json.dump(config, f)
        except Exception as e:
            self.notify(f"Error saving config: {e}", severity="error")

    def load_config(self):
        """Load selected_language and selected_level from config.json."""
        env_path = os.path.join(get_config_dir(), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        if os.path.exists(get_config_path()):
            try:
                with open(get_config_path(), "r") as f:
                    config = json.load(f)
                self.selected_language = config.get(
                    "selected_language", self.selected_language
                )
                self.selected_level = config.get("selected_level", self.selected_level)
                # Set the selected values in the Select widgets
                language_select = self.query_one("#language-select", Select)
                level_select = self.query_one("#level-select", Select)
                language_select.value = self.selected_language
                level_select.value = self.selected_level
                self.notify(
                    f"Loaded config: Language={self.selected_language}, Level={self.selected_level}"
                )
            except Exception as e:
                self.notify(f"Error loading config: {e}", severity="error")

    def save_state(self):
        """Save the current application state to state.json."""
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
            self.notify("State saved successfully.")
        except Exception as e:
            self.notify(f"Error saving state: {e}", severity="error")

    def load_state(self):
        """Load the application state from state.json."""
        if not os.path.exists(get_state_path()):
            self.notify("No saved state found.", severity="warning")
            return
        try:
            with open(get_state_path(), "r") as f:
                state = json.load(f)
            # Restore selections
            self.selected_language = state.get("selected_language", "")
            self._reload_definitions()

            self.selected_exercise = state.get("selected_exercise", "")
            self.selected_level = state.get("selected_level", "")
            self.generated_exercise = state.get("generated_exercise", "")
            self.generated_hints = state.get("generated_hints", "")
            self.writing_input = state.get("writing_input", "")
            self.writing_mistakes = state.get("mistakes", "")
            self.style_errors = state.get("style", "")
            self.recommendations = state.get("recs", "")

            # Restore Select widgets
            self.query_one("#language-select", Select).value = self.selected_language
            self.query_one("#exercise-select", Select).value = self.selected_exercise
            self.query_one("#level-select", Select).value = self.selected_level

            # Restore TextAreas and Markdown components
            self.query_one("#exercise-display", Markdown).update(
                self.generated_exercise
            )
            self.query_one("#hints-display", Markdown).update(self.generated_hints)
            self.query_one("#writing-input", TextArea).load_text(self.writing_input)
            self.query_one("#mistakes-display", Markdown).update(self.writing_mistakes)
            self.query_one("#style-display", Markdown).update(self.style_errors)
            self.query_one("#recs-display", Markdown).update(self.recommendations)

            self.notify("State loaded successfully.")
        except Exception as e:
            self.notify(f"Error loading state: {e}", severity="error")

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

            file_path = os.path.join(
                export_dir,
                f"{self.selected_language}_{self.selected_exercise}_{datetime_str}.md",
            ).replace(" ", "_").replace("/", "_")
            with open(file_path, "w") as f:
                f.write(md)
            self.notify(f"Exported to {file_path}")
        except Exception as e:
            self.notify(f"Error exporting markdown: {e}", severity="error")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Horizontal(id="app-grid"):
            with Vertical(id="left-pane"):
                yield Static("Language:", classes="label", shrink=True)
                yield Select(
                    LANGUAGES, id="language-select", prompt="Select Language..."
                )
                yield Static("Level:", classes="label")
                yield Select(LEVELS, id="level-select", prompt="Select Level...")
                yield Static("Exercise Type:", classes="label")
                yield Select(
                    self.excercise_types,
                    id="exercise-select",
                    prompt="Select Exercise...",
                )
                yield Button("Generate Exercise", id="generate-btn", variant="primary")
                yield Static("Exercise:", classes="label", id="exercise-label")
                yield Markdown(
                    self.generated_exercise,
                    id="exercise-display",
                    classes="display-area",
                )
                yield Static("Hints:", classes="label", id="hints-label")
                yield Markdown(
                    self.generated_hints, id="hints-display", classes="display-area"
                )
            with Vertical(id="right-pane"):
                yield Static("Your Writing:", classes="label")
                yield TextArea(id="writing-input", classes="input-area")
                yield Static("Word Count:", classes="label", id="word-count-label")
                yield Button("Check Writing", id="check-btn", variant="success")
                yield Static("Mistakes:", classes="label", id="mistakes-label")
                yield Markdown(id="mistakes-display", classes="feedback-area")
                yield Static("Stylistic Errors:", classes="label", id="style-label")
                yield Markdown(id="style-display", classes="feedback-area")
                yield Static("Recommendations:", classes="label", id="recs-label")
                yield Markdown(id="recs-display", classes="feedback-area")
        yield Footer()

    # --- Event Handlers ---

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Configure LiteLLM to use OpenRouter
        litellm.api_key = os.getenv("OPENROUTER_API_KEY")
        litellm.base_url = (
            "https://openrouter.ai/api/v1"  # Or the specific OpenRouter endpoint
        )

        self.load_config()  # Restore config on start
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            litellm.api_key = api_key
        if not litellm.api_key:
            self.notify(
                "Error: OPENROUTER_API_KEY not found in .env file. Please configure it in Settings (Ctrl+,).",
                severity="error",
                timeout=10,
            )

    def _update_word_count(self) -> None:
        """Update the word count label."""
        text_area = self.query_one("#writing-input", TextArea)
        word_count = len(text_area.text.split())
        if (
            self.selected_exercise == ""
            or self.selected_exercise not in self.excercise_definitions
        ):
            self.query_one("#word-count-label", Static).update(
                f"Word Count: {word_count}"
            )
        else:
            self.query_one("#word-count-label", Static).update(
                f"Word Count: {word_count}, min {self.excercise_definitions[self.selected_exercise]['expected_length'][0]}, max {self.excercise_definitions[self.selected_exercise]['expected_length'][1]}"
            )
            if (
                word_count
                < self.excercise_definitions[self.selected_exercise]["expected_length"][
                    0
                ]
                or word_count
                > self.excercise_definitions[self.selected_exercise]["expected_length"][
                    1
                ]
            ):
                self.query_one("#word-count-label", Static).classes = "red"
            else:
                self.query_one("#word-count-label", Static).classes = ""
        self.query_one("#word-count-label", Static).refresh()

    def on_text_area_changed(self, event) -> None:
        """Handle changes in the TextArea for writing input."""
        if event.text_area.id == "writing-input":
            self.writing_input = event.text_area.text
            self._update_word_count()

    def _reload_definitions(self) -> None:
        """Reload exercise definitions based on the selected language."""
        self.excercise_types = self.excercise_types_all.get(self.selected_language, [])
        self.excercise_definitions = self.excercise_definitions_all.get(
            self.selected_language, {}
        )
        # Update the exercise select options
        exercise_select = self.query_one("#exercise-select", Select)
        exercise_select.set_options(self.excercise_types)

        exercise_select.refresh()

    def on_select_changed(self, event) -> None:
        """Handle changes in the Select widgets."""
        if event.select.id == "language-select":
            self.selected_language = event.value
            self._reload_definitions()
            self.save_config()  # Save on change
            self.notify(f"Language set to: {event.value}")
        elif event.select.id == "exercise-select":
            self.selected_exercise = event.value
            self.notify(f"Exercise type set to: {event.value}")
            # Update the expected length in the word count label
            self._update_word_count()
        elif event.select.id == "level-select":
            self.selected_level = event.value
            self.save_config()  # Save on change
            self.notify(f"Level set to: {event.value}")

    async def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "generate-btn":
            await self.action_generate_exercise()
        elif event.button.id == "check-btn":
            await self.action_check_writing()

    # --- Actions ---

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_save_state(self) -> None:
        """Save the current application state."""
        self.save_state()

    def action_load_state(self) -> None:
        """Load the application state."""
        self.load_state()

    def action_export_markdown(self) -> None:
        """Export the current state to Markdown."""
        self.export_markdown()

    def action_open_qa_screen(self) -> None:
        """Open the QA screen."""
        self.push_screen(QAScreen())

    def action_open_settings(self) -> None:
        """Open the settings screen."""
        self.push_screen(SettingsScreen())

    async def action_generate_exercise(self) -> None:
        """Generate a new exercise using LiteLLM."""
        if not self.selected_language or not self.selected_exercise:
            self.notify(
                "Please select both a language and an exercise type.",
                severity="warning",
            )
            return
        if not litellm.api_key:
            self.notify(
                "API Key not configured. Please set your OpenRouter API key in Settings (Ctrl+,).",
                severity="error",
            )
            return

        # Show loading state
        generate_btn = self.query_one("#generate-btn", Button)
        generate_btn.loading = True
        generate_btn.disabled = True
        self.query_one("#exercise-display", Markdown).update("Generating...")
        self.query_one("#hints-display", Markdown).update("")  # Clear previous hints

        self.notify(
            f"Generating '{self.selected_exercise}' exercise for {self.selected_language}...",
            timeout=5,
        )
        try:
            # Use utility function to generate exercise
            exercise_text, hints, cost = await generate_exercise(
                language=self.selected_language,
                level=self.selected_level,
                exercise_type=self.selected_exercise,
                definitions=self.excercise_definitions,
            )

            # Update stored values
            self.generated_exercise = exercise_text
            self.generated_hints = hints

            # Update TextAreas
            self.query_one("#exercise-display", Markdown).update(
                self.generated_exercise
            )
            self.query_one("#hints-display", Markdown).update(self.generated_hints)
            self.notify(f"Exercise generated! Cost: {cost:.4f} USD")

        except Exception as e:
            self.notify(f"Error generating exercise: {e}", severity="error", timeout=10)
            self.query_one("#exercise-display", Markdown).update(f"Error: {e}")
        finally:
            # Reset button state
            generate_btn.loading = False
            generate_btn.disabled = False

    async def action_check_writing(self) -> None:
        """Check the user's writing using LiteLLM."""
        self.writing_input = self.query_one("#writing-input", TextArea).text
        if not self.generated_exercise or not self.writing_input:
            self.notify(
                "Please generate an exercise and write something first.",
                severity="warning",
            )
            return
        if not litellm.api_key:
            self.notify(
                "API Key not configured. Please set your OpenRouter API key in Settings (Ctrl+,).",
                severity="error",
            )
            return

        # Show loading state
        check_btn = self.query_one("#check-btn", Button)
        check_btn.loading = True
        check_btn.disabled = True
        self.query_one("#mistakes-display", Markdown).update("Checking...")
        self.query_one("#style-display", Markdown).update("")
        self.query_one("#recs-display", Markdown).update("")

        self.notify("Checking your writing...", timeout=5)
        try:
            # Use utility function to check writing
            mistakes, style_errors, recommendations, cost = await check_writing(
                language=self.selected_language,
                level=self.selected_level,
                exercise_text=self.generated_exercise,
                writing_input=self.writing_input,
                exercise_type=self.selected_exercise,
                definitions=self.excercise_definitions,
            )

            # Update reactive variables
            self.writing_mistakes = mistakes
            self.style_errors = style_errors
            self.recommendations = recommendations

            # Update Markdown components
            self.query_one("#mistakes-display", Markdown).update(self.writing_mistakes)
            self.query_one("#style-display", Markdown).update(self.style_errors)
            self.query_one("#recs-display", Markdown).update(self.recommendations)
            self.notify(f"Feedback provided! Cost: {cost:.4f} USD")

        except Exception as e:
            self.notify(f"Error checking writing: {e}", severity="error", timeout=10)
            self.query_one("#mistakes-display", Markdown).update(f"Error: {e}")
        finally:
            # Reset button state
            check_btn.loading = False
            check_btn.disabled = False


def run_app():
    """Run the Language Tutor application."""
    app = LanguageTutorApp(
        excercise_types=exercise_types, excercise_definitions=definitions
    )
    app.run()

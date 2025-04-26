import datetime
import os
from dotenv import load_dotenv
import litellm
import re
import json  # <-- Add this import
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Button, Select, Static, TextArea
from textual.containers import Horizontal, Vertical
import random
from textual import events
from textual.app import App, ComposeResult
from textual.widgets import TextArea

from textual.reactive import var
from languages.polish import EXCERCISE_DEFINITIONS, EXERCISE_TYPES

# Load environment variables from .env file
load_dotenv()

# Configure LiteLLM to use OpenRouter
litellm.api_key = os.getenv("OPENROUTER_API_KEY")
litellm.base_url = "https://openrouter.ai/api/v1"  # Or the specific OpenRouter endpoint
#or_model_name = "openrouter/google/gemini-2.5-flash-preview:thinking"  # Example model, replace with your preferred model
or_model_name = "openrouter/google/gemini-2.5-flash-preview"  # Example model, replace with your preferred model
# --- Define available options ---
LANGUAGES = [
    ("Polish", "pl"),
    # ("Portuguese", "pt"),
    # ("English", "en"),
    # ("Spanish", "es"),
    # ("French", "fr"),
    # ("German", "de"),
    # Add more languages as needed
]


LEVELS = [
    ("Beginner", "A1"),
    ("Elementary", "A2"),
    ("Intermediate", "B1"),
    ("Upper Intermediate", "B2"),
    ("Advanced", "C1"),
    ("Proficient", "C2"),
]

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")
EXPORT_PATH = os.path.join(os.path.dirname(__file__), "export")
if not os.path.exists(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)


class LanguageTutorApp(App):
    """A Textual app to help with foreign language writing exercises."""

    BINDINGS = [
        ("ctrl+s", "save_state", "Save"),
        ("ctrl+l", "load_state", "Load"),
        ("ctrl+e", "export_markdown", "Export Markdown"),
    ]

    CSS_PATH = "styles.tcss"  # We'll create this file later

    # Reactive variables to store selections and generated content
    selected_language = var("")
    selected_exercise = var("")
    selected_level = var("")
    generated_exercise = var("")
    generated_hints = var("")

    def save_config(self):
        """Save selected_language and selected_level to config.json."""
        config = {
            "selected_language": self.selected_language,
            "selected_level": self.selected_level,
        }
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(config, f)
        except Exception as e:
            self.notify(f"Error saving config: {e}", severity="error")

    def load_config(self):
        """Load selected_language and selected_level from config.json."""
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    config = json.load(f)
                self.selected_language = config.get("selected_language", self.selected_language)
                self.selected_level = config.get("selected_level", self.selected_level)
                # Set the selected values in the Select widgets
                language_select = self.query_one("#language-select", Select)
                level_select = self.query_one("#level-select", Select)
                language_select.value = self.selected_language
                level_select.value = self.selected_level
                self.notify(f"Loaded config: Language={self.selected_language}, Level={self.selected_level}")
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
                "writing_input": self.query_one("#writing-input", TextArea).text,
                "mistakes": self.query_one("#mistakes-display", TextArea).text,
                "style": self.query_one("#style-display", TextArea).text,
                "recs": self.query_one("#recs-display", TextArea).text,
            }
            with open(STATE_PATH, "w") as f:
                json.dump(state, f)
            self.notify("State saved successfully.")
        except Exception as e:
            self.notify(f"Error saving state: {e}", severity="error")

    def load_state(self):
        """Load the application state from state.json."""
        if not os.path.exists(STATE_PATH):
            self.notify("No saved state found.", severity="warning")
            return
        try:
            with open(STATE_PATH, "r") as f:
                state = json.load(f)
            # Restore selections
            self.selected_language = state.get("selected_language", "")
            self.selected_exercise = state.get("selected_exercise", "")
            self.selected_level = state.get("selected_level", "")
            self.generated_exercise = state.get("generated_exercise", "")
            self.generated_hints = state.get("generated_hints", "")
            # Restore Select widgets
            self.query_one("#language-select", Select).value = self.selected_language
            self.query_one("#exercise-select", Select).value = self.selected_exercise
            self.query_one("#level-select", Select).value = self.selected_level
            # Restore TextAreas
            self.query_one("#exercise-display", TextArea).load_text(self.generated_exercise)
            self.query_one("#hints-display", TextArea).load_text(self.generated_hints)
            self.query_one("#writing-input", TextArea).load_text(state.get("writing_input", ""))
            self.query_one("#mistakes-display", TextArea).load_text(state.get("mistakes", ""))
            self.query_one("#style-display", TextArea).load_text(state.get("style", ""))
            self.query_one("#recs-display", TextArea).load_text(state.get("recs", ""))
            self.notify("State loaded successfully.")
        except Exception as e:
            self.notify(f"Error loading state: {e}", severity="error")

    def export_markdown(self):
        """Export the current exercise, writing, and feedback to a Markdown file."""
        try:
            exercise = self.generated_exercise or ""
            hints = self.generated_hints or ""
            writing = self.query_one("#writing-input", TextArea).text or ""
            mistakes = self.query_one("#mistakes-display", TextArea).text or ""
            style = self.query_one("#style-display", TextArea).text or ""
            recs = self.query_one("#recs-display", TextArea).text or ""

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
            file_path = os.path.join(EXPORT_PATH, f"{self.selected_language}_{self.selected_exercise}_{datetime_str}.md")
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
                yield Static("Language:", classes="label")
                yield Select(LANGUAGES, id="language-select", prompt="Select Language...")
                yield Static("Level:", classes="label")
                yield Select(LEVELS, id="level-select", prompt="Select Level...")
                yield Static("Exercise Type:", classes="label")
                yield Select(EXERCISE_TYPES, id="exercise-select", prompt="Select Exercise...")
                yield Button("Generate Exercise", id="generate-btn", variant="primary")
                yield Static("Exercise:", classes="label", id="exercise-label")
                yield TextArea(self.generated_exercise, read_only=True, id="exercise-display", classes="display-area")
                yield Static("Hints:", classes="label", id="hints-label")
                yield TextArea(self.generated_hints, read_only=True, id="hints-display", classes="display-area")
            with Vertical(id="right-pane"):
                yield Static("Your Writing:", classes="label")
                yield TextArea(id="writing-input", classes="input-area")
                yield Static("Word Count:", classes="label", id="word-count-label")
                yield Button("Check Writing", id="check-btn", variant="success")
                yield Static("Mistakes:", classes="label", id="mistakes-label")
                yield TextArea(read_only=True, id="mistakes-display", classes="feedback-area")
                yield Static("Stylistic Errors:", classes="label", id="style-label")
                yield TextArea(read_only=True, id="style-display", classes="feedback-area")
                yield Static("Recommendations:", classes="label", id="recs-label")
                yield TextArea(read_only=True, id="recs-display", classes="feedback-area")
        yield Footer()

    # --- Event Handlers ---

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.load_config()  # Restore config on start
        if not litellm.api_key:
            self.notify("Error: OPENROUTER_API_KEY not found in .env file.", severity="error", timeout=10)

    def _update_word_count(self) -> None:
        """Update the word count label."""
        text_area = self.query_one("#writing-input", TextArea)
        word_count = len(text_area.text.split())
        if self.selected_exercise == "":
            self.query_one("#word-count-label", Static).update(f"Word Count: {word_count}")
        else:
            self.query_one("#word-count-label", Static).update(f"Word Count: {word_count}, min {EXCERCISE_DEFINITIONS[self.selected_exercise]['expected_length'][0]}, max {EXCERCISE_DEFINITIONS[self.selected_exercise]['expected_length'][1]}")
            if word_count < EXCERCISE_DEFINITIONS[self.selected_exercise]['expected_length'][0] or word_count > EXCERCISE_DEFINITIONS[self.selected_exercise]['expected_length'][1]:
                self.query_one("#word-count-label", Static).classes = "red"
            else:
                self.query_one("#word-count-label", Static).classes = ""
        self.query_one("#word-count-label", Static).refresh()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle changes in the TextArea for writing input."""
        if event.text_area.id == "writing-input":
            self._update_word_count()
                
        
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle changes in the Select widgets."""
        if event.select.id == "language-select":
            self.selected_language = event.value
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

    async def on_button_pressed(self, event: Button.Pressed) -> None:
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

    async def action_generate_exercise(self) -> None:
        """Generate a new exercise using LiteLLM."""
        if not self.selected_language or not self.selected_exercise:
            self.notify("Please select both a language and an exercise type.", severity="warning")
            return
        if not litellm.api_key:
            self.notify("API Key not configured. Cannot generate exercise.", severity="error")
            return

        # Show loading state
        generate_btn = self.query_one("#generate-btn", Button)
        generate_btn.loading = True
        generate_btn.disabled = True
        self.query_one("#exercise-display", TextArea).load_text("Generating...")
        self.query_one("#hints-display", TextArea).load_text("")  # Clear previous hints

        self.notify(f"Generating '{self.selected_exercise}' exercise for {self.selected_language}...", timeout=5)
        try:
            # Construct prompt asking for specific formatting
            prompt = f"""Create a short '{self.selected_exercise}' writing exercise for a learner of {self.selected_language} for a proficiency level {self.selected_level}.
            The expected length of the writing should be between {EXCERCISE_DEFINITIONS[self.selected_exercise]['expected_length'][0]} and {EXCERCISE_DEFINITIONS[self.selected_exercise]['expected_length'][1]} words.
            Random number is {random.randint(1, 10000)} (don't use it, it is just to make the prompt different). 
Provide the exercise text and optionally some hints. The requirements for the exercise are:
'{EXCERCISE_DEFINITIONS[self.selected_exercise]['requirements']}'
You should generate exactly one exercise.

Format the output EXACTLY like this, using these specific headings:

**Exercise:**
[The exercise text goes here]

**Hints:**
[Optional hints go here. If no hints, write "None."]
"""
            messages = [{"role": "user", "content": prompt}]

            # Replace with your preferred model on OpenRouter
            # Make sure the model is available via your OpenRouter setup
            model_name = or_model_name  # Example model

            # Make the async API call
            response = await litellm.acompletion(model=model_name, messages=messages, api_base=litellm.base_url)
            full_response_content = response.choices[0].message.content

            # --- Basic Parsing ---
            exercise_match = re.search(r"\*\*Exercise:\*\*\n(.*?)\n\*\*Hints:\*\*", full_response_content, re.DOTALL | re.IGNORECASE)
            hints_match = re.search(r"\*\*Hints:\*\*\n(.*)", full_response_content, re.DOTALL | re.IGNORECASE)

            if exercise_match:
                self.generated_exercise = exercise_match.group(1).strip()
            else:
                # Fallback if parsing fails
                self.generated_exercise = full_response_content.split("**Hints:**")[0].replace("**Exercise:**", "").strip()
                self.notify("Could not precisely parse exercise, showing raw response part.", severity="warning")

            if hints_match:
                self.generated_hints = hints_match.group(1).strip()
                if self.generated_hints.lower() == "none.":
                    self.generated_hints = ""  # Clear if hints are explicitly none
            else:
                # Fallback if parsing fails
                self.generated_hints = ""  # Assume no hints if parsing fails

            # Update TextAreas
            self.query_one("#exercise-display", TextArea).load_text(self.generated_exercise)
            self.query_one("#hints-display", TextArea).load_text(self.generated_hints)
            self.notify("Exercise generated!")

        except Exception as e:
            self.notify(f"Error generating exercise: {e}", severity="error", timeout=10)
            self.query_one("#exercise-display", TextArea).load_text(f"Error: {e}")
        finally:
            # Reset button state
            generate_btn.loading = False
            generate_btn.disabled = False

    async def action_check_writing(self) -> None:
        """Check the user's writing using LiteLLM."""
        writing_input = self.query_one("#writing-input", TextArea).text
        if not self.generated_exercise or not writing_input:
            self.notify("Please generate an exercise and write something first.", severity="warning")
            return
        if not litellm.api_key:
            self.notify("API Key not configured. Cannot check writing.", severity="error")
            return

        # Show loading state
        check_btn = self.query_one("#check-btn", Button)
        check_btn.loading = True
        check_btn.disabled = True
        self.query_one("#mistakes-display", TextArea).load_text("Checking...")
        self.query_one("#style-display", TextArea).load_text("")
        self.query_one("#recs-display", TextArea).load_text("")

        self.notify("Checking your writing...", timeout=5)
        try:
            # Construct prompt for checking, asking for specific format
            prompt = f"""A student learning {self.selected_language} was given the exercise:
'{self.generated_exercise}' with the following requirements:
'{EXCERCISE_DEFINITIONS[self.selected_exercise]['requirements']}'

Their response was:
'{writing_input}'

Please check their writing. Provide feedback listing:
1. Grammatical mistakes.
2. Stylistic errors.
3. Recommendations for improvement.
4. Following the requirements of the exercise.
Format the output EXACTLY like this, using these specific headings:

**Mistakes:**
[List of grammatical mistakes, or "None." if none found]

**Stylistic Errors:**
[List of stylistic errors, or "None." if none found]

**Recommendations:**
[List of recommendations, or "None." if none found]
"""
            messages = [{"role": "user", "content": prompt}]
            model_name = or_model_name  # Or another suitable model

            # Make the async API call
            response = await litellm.acompletion(model=model_name, messages=messages, api_base=litellm.base_url)
            feedback_content = response.choices[0].message.content

            # --- Basic Parsing ---
            mistakes_match = re.search(r"\*\*Mistakes:\*\*\n(.*?)\n\*\*Stylistic Errors:\*\*", feedback_content, re.DOTALL | re.IGNORECASE)
            style_match = re.search(r"\*\*Stylistic Errors:\*\*\n(.*?)\n\*\*Recommendations:\*\*", feedback_content, re.DOTALL | re.IGNORECASE)
            recs_match = re.search(r"\*\*Recommendations:\*\*\n(.*)", feedback_content, re.DOTALL | re.IGNORECASE)

            mistakes = mistakes_match.group(1).strip() if mistakes_match else "Could not parse."
            style_errors = style_match.group(1).strip() if style_match else "Could not parse."
            recommendations = recs_match.group(1).strip() if recs_match else "Could not parse."

            # Update TextAreas
            self.query_one("#mistakes-display", TextArea).load_text(mistakes if mistakes.lower() != "none." else "")
            self.query_one("#style-display", TextArea).load_text(style_errors if style_errors.lower() != "none." else "")
            self.query_one("#recs-display", TextArea).load_text(recommendations if recommendations.lower() != "none." else "")
            self.notify("Feedback provided!")

        except Exception as e:
            self.notify(f"Error checking writing: {e}", severity="error", timeout=10)
            self.query_one("#mistakes-display", TextArea).load_text(f"Error: {e}")
        finally:
            # Reset button state
            check_btn.loading = False
            check_btn.disabled = False

if __name__ == "__main__":
    app = LanguageTutorApp()
    app.run()

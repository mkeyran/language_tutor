"""QA Screen module for language tutor application."""

import json
import os
from textual.containers import Horizontal, Vertical, Grid
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import Button, Select, Static, TextArea, Markdown, Footer, Header
from textual.binding import Binding
from language_tutor.config import AI_MODELS
from language_tutor.utils import answer_question
from language_tutor.llm import llm


class QuestionTextArea(TextArea):
    """A custom TextArea that sends the question when Ctrl+Enter is pressed."""

    BINDINGS = [
        Binding("ctrl+down", "submit_question", "Submit Question", priority=True),
    ]

    async def action_submit_question(self) -> None:
        """Submit the question when Ctrl+down is pressed."""
        self.notify("Submitting question...")
        await self.screen.action_send_question()


class QAScreen(Screen):
    """A modal screen for asking questions to the AI model."""

    # Reactive variables for the QA screen
    selected_model = var("")
    last_query = var("")
    last_response = var("")
    last_cost = var(0.0)

    BINDINGS = [
        ("escape", "app.pop_screen", "Close QA Screen"),
    ]

    def compose(self):
        """Create child widgets for the QA screen."""

        yield Header()
        yield Static("Select AI Model:", id="model-select-label", classes="label")
        yield Select(AI_MODELS, id="model-select", prompt="Select AI Model...")
        yield Static("Your Question:", classes="label")
        yield QuestionTextArea(id="question-input", classes="input-area")
        yield Button("Send", id="send-btn", variant="primary")
        yield Button("Clear", id="clear-btn")
        yield Static("Assistant's Answer:", classes="label")
        yield Markdown(id="answer-display", classes="qa-answer")

        yield Static("Cost:", id="cost-display", classes="cost-label")
        yield Button("Close", id="qa-close-btn")
        yield Footer()

    def on_mount(self):
        """Called when the screen is mounted."""
        # Try to load the previously selected model
        try:
            from language_tutor.config import get_config_path

            with open(get_config_path(), "r") as f:
                config = json.load(f)
                self.selected_model = config.get("qa_model", AI_MODELS[0][1])
                model_select = self.query_one("#model-select", Select)
                model_select.value = self.selected_model

            question_input = self.query_one("#question-input", QuestionTextArea)
            question_input.focus()

        except:
            # If loading fails, set the default model
            self.selected_model = AI_MODELS[0][1]

    def on_qa_close(self):
        """Handle the close action for the QA screen."""
        self.app.pop_screen()

    async def on_qa_send_question(self):
        """Handle the send question action."""
        await self.action_send_question()

    def on_select_changed(self, event):
        """Handle changes in the Select widgets."""
        if event.select.id == "model-select":
            self.selected_model = event.value
            # Save the selected model to config
            try:
                from language_tutor.config import get_config_path

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
                self.app.notify(f"Error saving model selection: {e}", severity="error")

    async def on_button_pressed(self, event):
        """Handle button presses."""
        if event.button.id == "send-btn":
            await self.action_send_question()
        elif event.button.id == "clear-btn":
            self.query_one("#question-input", TextArea).text = ""
            self.query_one("#answer-display", Markdown).text = ""
            self.query_one("#cost-display", Static).update("")
        elif event.button.id == "qa-close-btn":
            self.app.pop_screen()

    async def action_send_question(self):
        """Send the question to the AI model."""
        question = self.query_one("#question-input", TextArea).text
        if not question:
            self.app.notify("Please enter a question first.", severity="warning")
            return

        if not llm.is_configured():
            self.app.notify(
                "API Key not configured. Cannot send question.", severity="error"
            )
            return

        # Show loading state
        send_btn = self.query_one("#send-btn", Button)
        send_btn.loading = True
        send_btn.disabled = True
        self.query_one("#answer-display", Markdown).update("Generating answer...")

        self.app.notify("Sending your question to the AI...", timeout=3)

        try:
            # Get the current context from the parent app
            app = self.app
            context = {
                "language": app.selected_language,
                "level": app.selected_level,
                "exercise_type": app.selected_exercise,
                "exercise": app.generated_exercise,
            }

            # Use utility function to get answer
            answer, cost = await answer_question(
                model=self.selected_model, question=question, context=context
            )

            # Update cost display
            if cost:
                self.last_cost = cost
                self.query_one("#cost-display", Static).update(f"Cost: ${cost:.6f}")
            else:
                self.query_one("#cost-display", Static).update("Cost: unknown")

            # Display the response
            self.last_response = answer
            self.query_one("#answer-display", Markdown).update(answer)

        except Exception as e:
            self.app.notify(f"Error querying AI: {e}", severity="error", timeout=10)
            self.query_one("#answer-display", Markdown).update(f"Error: {e}")
        finally:
            # Reset button state
            send_btn.loading = False
            send_btn.disabled = False

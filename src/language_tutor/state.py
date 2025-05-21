from dataclasses import dataclass, asdict
import json
import os
from typing import Optional

from .config import get_state_path


@dataclass
class LanguageTutorState:
    """Container for application state."""

    selected_language: str = ""
    selected_exercise: str = ""
    selected_level: str = ""
    generated_exercise: str = ""
    generated_hints: str = ""
    writing_mistakes: str = ""
    style_errors: str = ""
    recommendations: str = ""
    writing_input: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: Optional[str] = None) -> None:
        """Serialize the state to JSON."""
        if path is None:
            path = get_state_path()
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "LanguageTutorState":
        """Load state from JSON file."""
        if path is None:
            path = get_state_path()
        if not os.path.exists(path):
            return cls()
        with open(path, "r") as f:
            data = json.load(f)
        return cls(**data)


    def to_markdown(self) -> str:
        """Return a Markdown representation of the current state."""
        exercise = self.generated_exercise or ""
        hints = self.generated_hints or ""
        writing = self.writing_input or ""
        mistakes = self.writing_mistakes or ""
        style = self.style_errors or ""
        recs = self.recommendations or ""
        return f"""# Language Tutor Export

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


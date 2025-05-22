from dataclasses import dataclass, asdict, field
import json
import os
from typing import Optional
import toml

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
    grammar_errors_raw: list = field(default_factory=list)
    style_errors_raw: list = field(default_factory=list)
    writing_input_html: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: Optional[str] = None) -> None:
        """Serialize the state to file.

        If the file extension is ``.json`` the state is stored as JSON,
        otherwise it is stored in ``toml`` format.  When ``path`` is
        omitted the default location returned by :func:`get_state_path`
        is used.
        """
        if path is None:
            path = get_state_path()
        ext = os.path.splitext(path)[1].lower()
        with open(path, "w") as f:
            if ext == ".json":
                json.dump(self.to_dict(), f)
            else:
                toml.dump(self.to_dict(), f)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "LanguageTutorState":
        """Load state from file.

        If the file extension is ``.json`` the state is interpreted as
        JSON, otherwise it is treated as ``toml``.
        """
        if path is None:
            path = get_state_path()
        if not os.path.exists(path):
            return cls()
        ext = os.path.splitext(path)[1].lower()
        with open(path, "r") as f:
            if ext == ".json":
                data = json.load(f)
            else:
                data = toml.load(f)
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


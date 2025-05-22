"""Configuration and constants for the Language Tutor app."""

import os
from litellm.types.utils import CostPerToken

# Default UI settings
DEFAULT_TEXT_FONT_SIZE = 14

# --- LiteLLM model names and prices ---
OR_MODEL_NAME = "openrouter/google/gemini-2.5-flash-preview-05-20"
OR_MODEL_NAME_CHECK = "openrouter/google/gemini-2.5-flash-preview-05-20:thinking"
# OR_MODEL_NAME_CHECK = "openrouter/openai/o3-mini"

MODEL_PRICE_PER_TOKEN = {
    "gemini-2.5-flash-preview-05-20": CostPerToken(
        input_cost_per_token=0.15 / 1e6, output_cost_per_token=0.6 / 1e6
    ),
    "gemini-2.5-flash-preview-05-20:thinking": CostPerToken(
        input_cost_per_token=0.15 / 1e6, output_cost_per_token=0.6 / 1e6
    ),
    "o3-mini": CostPerToken(
        input_cost_per_token=1.10 / 1e6, output_cost_per_token=4.40 / 1e6
    ),
}

# --- Available AI models for QA feature ---
AI_MODELS = [
    ("Gemini 2.5 Flash", "openrouter/google/gemini-2.5-flash-preview-05-20"),
    ("Claude 3 Opus", "openrouter/anthropic/claude-3-opus"),
    ("GPT-4o", "openrouter/openai/gpt-4o"),
    (
        "Gemini 2.5 Flash: Thinking",
        "openrouter/google/gemini-2.5-flash-preview-05-20:thinking",
    ),
]

# --- Supported languages and proficiency levels ---
LANGUAGES = [
    ("English", "en"),
    ("Polish", "pl"),
    ("Portuguese", "pt"),
]

LEVELS = [
    ("Beginner", "A1"),
    ("Elementary", "A2"),
    ("Intermediate", "B1"),
    ("Upper Intermediate", "B2"),
    ("Advanced", "C1"),
    ("Proficient", "C2"),
]


# --- File paths and configuration ---
def get_config_dir():
    """Get the configuration directory."""
    # Use standard XDG_CONFIG_HOME or fallback to ~/.config
    config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    app_config_dir = os.path.join(config_dir, "language-tutor")
    if not os.path.exists(app_config_dir):
        os.makedirs(app_config_dir)
    return app_config_dir


def get_config_path():
    """Get the path to the config file."""
    return os.path.join(get_config_dir(), "config.json")


def get_state_path():
    """Get the path to the state file."""
    return os.path.join(get_config_dir(), "state.json")


def get_export_path():
    """Get the path to the export directory."""
    path = os.environ.get(
        "LANGUAGE_TUTOR_EXPORT_PATH", "~/Documents/language-tutor-export"
    )
    if path.startswith("~"):
        path = os.path.expanduser(path)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

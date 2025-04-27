"""Configuration and constants for the Language Tutor app."""

import os
from litellm.types.utils import CostPerToken

# --- LiteLLM model names and prices ---
OR_MODEL_NAME = "openrouter/google/gemini-2.5-flash-preview"
OR_MODEL_NAME_CHECK = "openrouter/google/gemini-2.5-flash-preview:thinking"

MODEL_PRICE_PER_TOKEN = {
    "gemini-2.5-flash-preview": CostPerToken(input_cost_per_token=0.15/1e6, output_cost_per_token=0.6/1e6),
    "gemini-2.5-flash-preview:thinking": CostPerToken(input_cost_per_token=0.15/1e6, output_cost_per_token=0.6/1e6),
}

# --- Available AI models for QA feature ---
AI_MODELS = [
    ("Gemini 2.5 Flash", "openrouter/google/gemini-2.5-flash-preview"),
    ("Claude 3 Opus", "openrouter/anthropic/claude-3-opus"),
    ("GPT-4o", "openrouter/openai/gpt-4o"),
]

# --- Supported languages and proficiency levels ---
LANGUAGES = [
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
    return os.path.join(get_config_dir(), "export")
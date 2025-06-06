# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running Tests
```bash
uv run pytest tests/ -v
```

### Building the Package
```bash
uv build
```

### Installing for Development
```bash
uv pip install -e .
```

### Running the Application
```bash
language-tutor-ui
```

## Architecture Overview

### Core Components

**GUI Layer**: PyQt5-based GUI with main window (`LanguageTutorGUI`) and specialized dialogs for settings, Q&A, and Wiktionary lookup.

**State Management**: Centralized state in `LanguageTutorState` dataclass that handles persistence, export to Markdown, and tracks user progress across sessions.

**LLM Integration**: Pluggable backend system with abstract `LLM` base class. Default implementation uses LiteLLM with OpenRouter API for multi-model support. Global LLM instance accessible via `llm.py`.

**Language Support**: Modular language system where each language module (Polish, Portuguese, English) defines exercise types and prompts. Exercise types are dynamically loaded and include "Random" and "Custom" options.

**Exercise Generation**: AI-powered exercise generation and feedback system that adapts to user's selected language and proficiency level.

### Key Files

- `gui_app.py`: Main GUI application class with async integration via nest-asyncio
- `state.py`: Application state container with save/load/export functionality  
- `llm.py`: Global LLM interface and instance management
- `llms/`: LLM backend implementations (LiteLLM, OpenAI)
- `languages/`: Language-specific exercise definitions and types
- `config.py`: Configuration constants including model pricing and UI defaults

### Configuration

The app requires an `.env` file in `~/.config/language-tutor/` with:
```
OPENROUTER_API_KEY=your_api_key_here
```

Default models are configured in `config.py` using OpenRouter endpoints.
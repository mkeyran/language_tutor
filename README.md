# Language Tutor

A PyQt5-based GUI application for practicing writing in foreign languages with AI-powered feedback and interactive exercises.

## Features

- **Multi-language Support**: Practice writing in English, Polish, and Portuguese
- **AI-Powered Exercises**: Generate contextual writing prompts using advanced language models
- **Intelligent Feedback**: Get detailed writing corrections and suggestions from AI
- **Interactive Q&A**: Ask questions about language concepts with built-in AI assistant
- **Wiktionary Integration**: Quick word lookups with embedded browser
- **Progress Tracking**: Save and resume your writing sessions
- **Export Functionality**: Export exercises and feedback to Markdown format
- **Customizable Interface**: Adjustable font sizes and responsive design
- **Multiple Exercise Types**: Various exercise formats for different learning styles

## Installation

### Prerequisites

- Python 3.12 or higher
- OpenRouter API key (for AI features)

### Using uv (recommended)

```bash
uv pip install language-tutor
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/language-tutor.git
cd language-tutor
```

2. Install dependencies and package:
```bash
uv pip install -e .
```

### Development Installation

```bash
uv pip install -e ".[dev]"
```

## Configuration

1. Create the configuration directory:
```bash
mkdir -p ~/.config/language-tutor
```

2. Create a `.env` file with your API key:
```bash
echo "OPENROUTER_API_KEY=your_api_key_here" > ~/.config/language-tutor/.env
```

## Usage

Launch the application:

```bash
language-tutor-ui
```

### Getting Started

1. **Setup**: Configure your OpenRouter API key in settings
2. **Language Selection**: Choose your target language and proficiency level
3. **Exercise Type**: Select from available exercise types or create custom prompts
4. **Generate**: Click "Generate Exercise" to create AI-powered writing prompts
5. **Write**: Compose your response in the text editor
6. **Feedback**: Get AI-powered corrections and suggestions
7. **Save/Export**: Save your progress or export to Markdown

### Key Features

- **Q&A Dialog**: Ask language-related questions with dedicated AI assistant
- **Wiktionary Lookup**: Built-in dictionary with web browser integration
- **State Management**: Automatic session saving and loading
- **Keyboard Shortcuts**: Quick access to common functions

## Architecture

### Core Components

- **GUI Layer**: PyQt5-based interface with main window and specialized dialogs
- **State Management**: Centralized state handling with persistence and export capabilities
- **LLM Integration**: Pluggable AI backend system supporting multiple providers
- **Language Modules**: Modular language-specific exercise definitions
- **Exercise System**: Dynamic exercise generation and feedback processing

### Project Structure

```
language_tutor/
├── src/language_tutor/
│   ├── __init__.py
│   ├── gui.py              # Main GUI entry point
│   ├── gui_app.py          # Core application class
│   ├── state.py            # State management and persistence
│   ├── config.py           # Configuration and constants
│   ├── llm.py              # LLM interface and management
│   ├── exercise.py         # Exercise generation logic
│   ├── feedback_handler.py # Writing feedback processing
│   ├── gui_screens/        # GUI components
│   │   ├── qa_dialog.py    # Q&A interface
│   │   ├── settings_dialog.py # Settings management
│   │   └── wiktionary_dialog.py # Dictionary lookup
│   ├── languages/          # Language-specific modules
│   │   ├── english.py
│   │   ├── polish.py
│   │   └── portuguese.py
│   └── llms/              # LLM backend implementations
│       ├── base.py        # Abstract base class
│       ├── lite.py        # LiteLLM implementation
│       └── openai_impl.py # OpenAI implementation
├── tests/                 # Comprehensive test suite
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Building the Package

```bash
uv build
```

### Code Quality

The project includes comprehensive tests covering:
- Exercise generation and feedback
- State management and persistence
- LLM integration and responses
- GUI component functionality
- Language module behavior

### Configuration

Default models and pricing are configured in `config.py`. The application supports multiple AI providers through the LiteLLM library, with OpenRouter as the default backend.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest tests/ -v`
5. Submit a pull request

## License

MIT License - see the LICENSE file for details.
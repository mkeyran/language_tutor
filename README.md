# Language Tutor

A TUI (Text User Interface) application for practicing writing in foreign languages with AI-powered feedback.

## Features

- Support for multiple languages (currently Polish and Portuguese)
- Interactive writing exercises with AI-generated prompts
- AI-powered writing feedback and corrections
- Export exercises and feedback to Markdown
- Save and load your work sessions

## Installation

### Using uv (recommended)

```bash
uv pip install language-tutor
```

### From Source with uv

1. Clone the repository:
```bash
git clone https://github.com/yourusername/language-tutor.git
cd language-tutor
```

2. Install the package in development mode:
```bash
uv pip install -e .
```

## Usage

After installation, you can launch the application using:

```bash
language-tutor
```

### First-time setup

1. Create a `.env` file in your config directory (~/.config/language-tutor/) with your API key:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

2. Select your language and proficiency level
3. Choose an exercise type
4. Click "Generate Exercise" 
5. Write your response in the input area
6. Click "Check Writing" for AI-powered feedback

## Commands

- `Ctrl+S`: Save your current state
- `Ctrl+L`: Load your saved state
- `Ctrl+E`: Export your work to Markdown

## Project Structure

```
language_tutor/
├── src/
│   └── language_tutor/
│       ├── __init__.py
│       ├── app.py           # Main application code
│       ├── cli.py           # Command-line interface
│       ├── styles.tcss      # Textual CSS styles
│       └── languages/       # Language-specific modules
│           ├── __init__.py
│           ├── polish.py
│           └── portuguese.py
├── pyproject.toml           # Build configuration
└── README.md                # This file
```

## Development

To build the package with uv:

```bash
uv build
```

To install the package locally for development:

```bash
uv pip install -e .
```

## License

MIT
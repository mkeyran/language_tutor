#!/usr/bin/env python3
"""Command-line interface for Language Tutor application."""

import argparse
import sys
from language_tutor import __version__
from language_tutor.app import run_app


def main():
    """Main entry point for the language-tutor command."""
    parser = argparse.ArgumentParser(
        description="Language Tutor - A tool for language learning writing exercises"
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version information and exit"
    )

    args = parser.parse_args()

    if args.version:
        print(f"Language Tutor v{__version__}")
        return 0

    # Run the main application
    run_app()
    return 0


if __name__ == "__main__":
    sys.exit(main())
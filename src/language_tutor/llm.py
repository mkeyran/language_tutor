"""Convenience interface for working with language model backends."""

from __future__ import annotations

from .llms import LLM, LiteLLM, OpenAILLM


# Single instance of the configured LLM backend
llm: LLM = LiteLLM()


def use_llm(instance: LLM) -> None:
    """Replace the globally used LLM implementation."""
    global llm
    llm = instance


def get_llm() -> LLM:
    """Return the currently configured LLM instance."""
    return llm


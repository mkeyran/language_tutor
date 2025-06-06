"""LLM provider management with dependency injection."""

from __future__ import annotations

from .llms import LLM, LiteLLM, OpenAILLM


class LLMProvider:
    """Manages LLM instances and provides dependency injection."""
    
    def __init__(self, default_llm: LLM | None = None):
        """Initialize with optional default LLM."""
        self._llm = default_llm or LiteLLM()
    
    def get_llm(self) -> LLM:
        """Get the current LLM instance."""
        return self._llm
    
    def set_llm(self, llm: LLM) -> None:
        """Set a new LLM instance."""
        self._llm = llm


# Default provider instance - can be replaced for testing or different configurations
default_provider = LLMProvider()


def get_llm() -> LLM:
    """Get the current LLM instance from the default provider."""
    return default_provider.get_llm()


def set_llm(llm: LLM) -> None:
    """Set the LLM instance in the default provider."""
    default_provider.set_llm(llm)


def create_provider(llm: LLM | None = None) -> LLMProvider:
    """Create a new LLM provider instance."""
    return LLMProvider(llm)


# Backward compatibility
use_llm = set_llm


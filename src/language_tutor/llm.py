"""Convenience interface for working with language model backends."""

from __future__ import annotations

from typing import Any, List, Tuple, Optional

from .llms import LLM, LiteLLM, OpenAILLM


# Default to LiteLLM implementation
_active_llm: LLM = LiteLLM()


def use_llm(instance: LLM) -> None:
    """Set the globally used LLM implementation."""
    global _active_llm
    _active_llm = instance


def get_llm() -> LLM:
    """Return the currently active LLM implementation."""
    return _active_llm


# Convenience wrappers for backwards compatibility

def set_api_key(key: str) -> None:
    _active_llm.set_api_key(key)


def get_api_key() -> str:
    return _active_llm.get_api_key()


def is_configured() -> bool:
    return _active_llm.is_configured()


def set_base_url(url: str) -> None:
    _active_llm.set_base_url(url)


def get_base_url() -> str:
    return _active_llm.get_base_url()


async def completion(model: str, messages: List[dict], **kwargs: Any) -> Tuple[Any, Optional[float]]:
    return await _active_llm.completion(model=model, messages=messages, **kwargs)

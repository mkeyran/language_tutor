from __future__ import annotations

"""Abstractions for interacting with different language model libraries."""

from abc import ABC, abstractmethod
import os
from typing import Any, List, Tuple, Optional

from .config import MODEL_PRICE_PER_TOKEN


class LLM(ABC):
    """Abstract interface for language model integrations."""

    @abstractmethod
    def set_api_key(self, key: str) -> None:
        """Configure the API key used for LLM calls."""

    @abstractmethod
    def get_api_key(self) -> str:
        """Return the configured API key."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Return ``True`` if an API key has been set."""

    @abstractmethod
    def set_base_url(self, url: str) -> None:
        """Set the base URL for API requests."""

    @abstractmethod
    def get_base_url(self) -> str:
        """Return the base URL for API requests."""

    @abstractmethod
    async def completion(self, model: str, messages: List[dict], **kwargs: Any) -> Tuple[Any, Optional[float]]:
        """Run an asynchronous completion.

        Returns the raw response object along with a floating point cost if
        available. Implementations may return ``None`` for the cost if it cannot
        be calculated.
        """


class LiteLLM(LLM):
    """Adapter that uses the :mod:`litellm` package."""

    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self) -> None:
        import litellm  # local import to avoid unnecessary dependency at import time

        self._litellm = litellm
        self._litellm.api_key = os.getenv("OPENROUTER_API_KEY", self._litellm.api_key)
        self._litellm.base_url = os.getenv("OPENROUTER_BASE_URL", self.DEFAULT_BASE_URL)

    def set_api_key(self, key: str) -> None:
        self._litellm.api_key = key
        os.environ["OPENROUTER_API_KEY"] = key

    def get_api_key(self) -> str:
        return self._litellm.api_key or ""

    def is_configured(self) -> bool:
        return bool(self._litellm.api_key)

    def set_base_url(self, url: str) -> None:
        self._litellm.base_url = url
        os.environ["OPENROUTER_BASE_URL"] = url

    def get_base_url(self) -> str:
        return self._litellm.base_url

    async def completion(self, model: str, messages: List[dict], **kwargs: Any) -> Tuple[Any, Optional[float]]:
        response = await self._litellm.acompletion(
            model=model,
            messages=messages,
            api_base=self._litellm.base_url,
            **kwargs,
        )

        from litellm import completion_cost

        model_name = model.split("/")[-1].split(":")[0]
        cost_info = MODEL_PRICE_PER_TOKEN.get(model_name)
        cost = completion_cost(response, custom_cost_per_token=cost_info) if cost_info else None
        return response, cost


class OpenAILLM(LLM):
    """Adapter for the :mod:`openai` library."""

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(self) -> None:
        self._api_key = os.getenv("OPENAI_API_KEY", "")
        self._base_url = os.getenv("OPENAI_BASE_URL", self.DEFAULT_BASE_URL)

    def set_api_key(self, key: str) -> None:
        self._api_key = key
        os.environ["OPENAI_API_KEY"] = key

    def get_api_key(self) -> str:
        return self._api_key

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def set_base_url(self, url: str) -> None:
        self._base_url = url
        os.environ["OPENAI_BASE_URL"] = url

    def get_base_url(self) -> str:
        return self._base_url

    async def completion(self, model: str, messages: List[dict], **kwargs: Any) -> Tuple[Any, Optional[float]]:
        try:
            import openai  # type: ignore
        except Exception as exc:  # pragma: no cover - openai optional
            raise RuntimeError("openai library is required for OpenAILLM") from exc

        openai.api_key = self._api_key
        if hasattr(openai, "api_base"):
            openai.api_base = self._base_url  # type: ignore[attr-defined]
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=messages,
            **kwargs,
        )
        # The openai library doesn't provide cost calculation directly
        cost = None
        return response, cost


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

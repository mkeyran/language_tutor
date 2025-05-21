from __future__ import annotations

"""OpenAI library implementation of the :class:`LLM` interface."""

import os
from typing import Any, List, Tuple, Optional

from .base import LLM


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

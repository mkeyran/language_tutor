from __future__ import annotations

"""LiteLLM implementation of the :class:`LLM` interface."""

import os
from typing import Any, List, Tuple, Optional

from .base import LLM
from ..config import MODEL_PRICE_PER_TOKEN


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

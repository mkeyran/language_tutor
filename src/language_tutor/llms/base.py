from __future__ import annotations

"""Abstract interfaces for language model integrations."""

from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Optional


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

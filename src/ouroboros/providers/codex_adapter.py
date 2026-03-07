"""Codex adapter for Codex-native LLM completion.

This adapter is a thin wrapper over LiteLLMAdapter and enforces the
Codex provider contract:
- Auth source is OPENAI_API_KEY
- Model from CompletionConfig is passed through unchanged
- Retry behavior is inherited from LiteLLMAdapter
- Expected failures are normalized to ProviderError(provider="codex")
"""

from __future__ import annotations

from ouroboros.core.errors import ProviderError
from ouroboros.core.types import Result
from ouroboros.providers.base import CompletionConfig, CompletionResponse, Message
from ouroboros.providers.litellm_adapter import LiteLLMAdapter


class CodexAdapter:
    """LLM adapter for Codex primary-path runtime."""

    def __init__(
        self,
        *,
        api_base: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize Codex adapter.

        Args:
            api_base: Optional API base URL for custom endpoints.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for transient errors.
        """
        self._delegate = LiteLLMAdapter(
            api_base=api_base,
            timeout=timeout,
            max_retries=max_retries,
        )

    async def complete(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> Result[CompletionResponse, ProviderError]:
        """Make a completion request through LiteLLM with Codex semantics."""
        try:
            result = await self._delegate.complete(messages, config)
        except Exception as exc:
            return Result.err(
                ProviderError(
                    f"Unexpected error: {exc}",
                    provider="codex",
                    details={"original_exception": type(exc).__name__},
                )
            )

        if result.is_ok:
            return result

        original = result.error
        details = dict(original.details)
        if original.provider and original.provider != "codex":
            details["upstream_provider"] = original.provider
        return Result.err(
            ProviderError(
                original.message,
                provider="codex",
                status_code=original.status_code,
                details=details,
            )
        )

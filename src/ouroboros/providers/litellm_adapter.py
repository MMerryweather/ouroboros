"""LiteLLM adapter for unified LLM provider access.

This module provides the LiteLLMAdapter class that implements the LLMAdapter
protocol using LiteLLM for multi-provider support including OpenRouter.
"""

import os
from typing import Any

import litellm
import stamina
import structlog

from ouroboros.config.loader import load_credentials
from ouroboros.core.errors import ProviderError
from ouroboros.core.security import MAX_LLM_RESPONSE_LENGTH, InputValidator
from ouroboros.core.types import Result
from ouroboros.providers.base import (
    CompletionConfig,
    CompletionResponse,
    Message,
    UsageInfo,
)

log = structlog.get_logger()

# LiteLLM exceptions that should trigger retries
RETRIABLE_EXCEPTIONS = (
    litellm.RateLimitError,
    litellm.ServiceUnavailableError,
    litellm.Timeout,
    litellm.APIConnectionError,
)


class LiteLLMAdapter:
    """LLM adapter using LiteLLM for unified provider access.

    This adapter supports multiple LLM providers through LiteLLM's unified
    interface, including OpenRouter for model routing.

    API keys are loaded from environment variables with the following priority:
    1. Environment variables: OPENROUTER_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
    2. Explicit api_key parameter (overrides environment)

    Example:
        # Using environment variables (recommended)
        adapter = LiteLLMAdapter()

        # Or with explicit API key
        adapter = LiteLLMAdapter(api_key="sk-...")

        result = await adapter.complete(
            messages=[Message(role=MessageRole.USER, content="Hello!")],
            config=CompletionConfig(model="openrouter/openai/gpt-4"),
        )
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_base: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize the LiteLLM adapter.

        Args:
            api_key: Optional API key (overrides environment variables).
            api_base: Optional API base URL for custom endpoints.
            timeout: Request timeout in seconds. Default 60.0.
            max_retries: Maximum number of retries for transient errors. Default 3.
        """
        self._api_key = api_key
        self._api_base = api_base
        self._timeout = timeout
        self._max_retries = max_retries

    def _get_api_key(self, model: str) -> str | None:
        """Get the appropriate API key for the model.

        Priority:
        1. Explicit api_key from constructor
        2. Environment variables based on model prefix

        Args:
            model: The model identifier.

        Returns:
            The API key or None if not found.
        """
        if self._api_key:
            return self._api_key

        provider = self._extract_provider(model)

        # Check environment variables based on model prefix
        if provider == "openrouter":
            env_key = os.environ.get("OPENROUTER_API_KEY")
        elif provider == "anthropic":
            env_key = os.environ.get("ANTHROPIC_API_KEY")
        elif provider == "openai":
            env_key = os.environ.get("OPENAI_API_KEY")
        else:
            env_key = os.environ.get("OPENROUTER_API_KEY")
        if env_key:
            return env_key

        # Fallback to credentials.yaml if env var is absent.
        try:
            credentials = load_credentials()
        except Exception:
            return None

        provider_creds = credentials.providers.get(provider)
        if provider_creds and provider_creds.api_key and not provider_creds.api_key.startswith("YOUR_"):
            return provider_creds.api_key

        # Unknown providers default to openrouter credentials.
        if provider == "unknown":
            openrouter_creds = credentials.providers.get("openrouter")
            if openrouter_creds and openrouter_creds.api_key and not openrouter_creds.api_key.startswith(
                "YOUR_"
            ):
                return openrouter_creds.api_key

        return None

    def _build_completion_kwargs(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> dict[str, Any]:
        """Build the kwargs for litellm.acompletion.

        Args:
            messages: The conversation messages.
            config: The completion configuration.

        Returns:
            Dictionary of kwargs for litellm.acompletion.
        """
        kwargs: dict[str, Any] = {
            "model": config.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": self._normalize_temperature(config.model, config.temperature),
            "max_tokens": config.max_tokens,
            "timeout": self._timeout,
        }
        if self._supports_top_p(config.model):
            kwargs["top_p"] = config.top_p

        if config.stop:
            kwargs["stop"] = config.stop

        api_key = self._get_api_key(config.model)
        if api_key:
            kwargs["api_key"] = api_key

        if self._api_base:
            kwargs["api_base"] = self._api_base

        return kwargs

    def _supports_top_p(self, model: str) -> bool:
        """Return whether top_p should be sent for the given model."""
        # OpenAI GPT-5 models currently reject top_p.
        return not self._is_openai_gpt5_model(model)

    def _normalize_temperature(self, model: str, temperature: float) -> float:
        """Return a model-compatible temperature value."""
        # OpenAI GPT-5 models currently only support temperature=1.
        if self._is_openai_gpt5_model(model):
            return 1.0
        return temperature

    def _is_openai_gpt5_model(self, model: str) -> bool:
        """Check whether a model string refers to an OpenAI GPT-5 family model."""
        normalized_model = model.lower()
        return normalized_model.startswith("gpt-5") or normalized_model.startswith(
            "openai/gpt-5"
        )

    async def _raw_complete(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> litellm.ModelResponse:
        """Make the raw completion call with stamina retry.

        This method is decorated with stamina retry for transient errors.
        Exceptions bubble up for stamina to handle.

        Args:
            messages: The conversation messages.
            config: The completion configuration.

        Returns:
            The raw LiteLLM response.

        Raises:
            litellm exceptions for API errors.
        """
        kwargs = self._build_completion_kwargs(messages, config)

        log.debug(
            "llm.request.started",
            model=config.model,
            message_count=len(messages),
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        response = await litellm.acompletion(**kwargs)

        log.debug(
            "llm.request.completed",
            model=config.model,
            finish_reason=response.choices[0].finish_reason,
        )

        return response

    def _parse_response(
        self,
        response: litellm.ModelResponse,
        config: CompletionConfig,
    ) -> CompletionResponse:
        """Parse the LiteLLM response into CompletionResponse.

        Args:
            response: The raw LiteLLM response.
            config: The completion configuration.

        Returns:
            Parsed CompletionResponse.
        """
        choice = response.choices[0]
        usage = response.usage
        content = choice.message.content or ""

        # Security: Validate LLM response length to prevent DoS
        is_valid, error_msg = InputValidator.validate_llm_response(content)
        if not is_valid:
            log.warning(
                "llm.response.truncated",
                model=config.model,
                original_length=len(content),
                max_length=MAX_LLM_RESPONSE_LENGTH,
            )
            # Truncate oversized responses instead of failing
            content = content[:MAX_LLM_RESPONSE_LENGTH]

        return CompletionResponse(
            content=content,
            model=response.model or config.model,
            usage=UsageInfo(
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
            ),
            finish_reason=choice.finish_reason or "stop",
            raw_response=response.model_dump() if hasattr(response, "model_dump") else {},
        )

    async def complete(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> Result[CompletionResponse, ProviderError]:
        """Make a completion request to the LLM provider.

        This method handles retries internally using stamina and converts
        all expected failures to Result.err(ProviderError).

        Args:
            messages: The conversation messages to send.
            config: Configuration for the completion request.

        Returns:
            Result containing either the completion response or a ProviderError.
        """

        # Create the retry-decorated function with instance's max_retries
        @stamina.retry(
            on=RETRIABLE_EXCEPTIONS,
            attempts=self._max_retries,
            wait_initial=1.0,
            wait_max=10.0,
            wait_jitter=1.0,
        )
        async def _with_retry() -> litellm.ModelResponse:
            return await self._raw_complete(messages, config)

        try:
            response = await _with_retry()
            return Result.ok(self._parse_response(response, config))
        except RETRIABLE_EXCEPTIONS as e:
            # All retries exhausted
            log.warning(
                "llm.request.failed.retries_exhausted",
                model=config.model,
                error=str(e),
                max_retries=self._max_retries,
            )
            return Result.err(
                ProviderError.from_exception(e, provider=self._extract_provider(config.model))
            )
        except litellm.APIError as e:
            # Non-retriable API error
            log.warning(
                "llm.request.failed.api_error",
                model=config.model,
                error=str(e),
                status_code=getattr(e, "status_code", None),
            )
            return Result.err(
                ProviderError.from_exception(e, provider=self._extract_provider(config.model))
            )
        except litellm.AuthenticationError as e:
            log.warning(
                "llm.request.failed.auth_error",
                model=config.model,
                error=str(e),
            )
            return Result.err(
                ProviderError(
                    "Authentication failed - check API key",
                    provider=self._extract_provider(config.model),
                    status_code=401,
                    details={"original_exception": type(e).__name__},
                )
            )
        except litellm.BadRequestError as e:
            log.warning(
                "llm.request.failed.bad_request",
                model=config.model,
                error=str(e),
            )
            return Result.err(
                ProviderError.from_exception(e, provider=self._extract_provider(config.model))
            )
        except Exception as e:
            # Unexpected error - log and convert to ProviderError
            log.exception(
                "llm.request.failed.unexpected",
                model=config.model,
                error=str(e),
            )
            return Result.err(
                ProviderError(
                    f"Unexpected error: {e!s}",
                    provider=self._extract_provider(config.model),
                    details={"original_exception": type(e).__name__},
                )
            )

    def _extract_provider(self, model: str) -> str:
        """Extract the provider name from a model string.

        Args:
            model: The model identifier (e.g., 'openrouter/openai/gpt-4').

        Returns:
            The provider name (e.g., 'openrouter').
        """
        if "/" in model:
            return model.split("/")[0]
        # Common model prefixes
        if model.startswith("gpt"):
            return "openai"
        if model.startswith("claude"):
            return "anthropic"
        return "unknown"

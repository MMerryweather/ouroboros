"""Unit tests for ouroboros.providers.codex_adapter module."""

from unittest.mock import AsyncMock, patch

from ouroboros.core.errors import ProviderError
from ouroboros.core.types import Result
from ouroboros.providers.base import (
    CompletionConfig,
    CompletionResponse,
    Message,
    MessageRole,
    UsageInfo,
)
from ouroboros.providers.codex_adapter import CodexAdapter


def _sample_messages() -> list[Message]:
    return [Message(role=MessageRole.USER, content="Hello")]


def _sample_config() -> CompletionConfig:
    return CompletionConfig(model="openai/gpt-5")


def _sample_response() -> CompletionResponse:
    return CompletionResponse(
        content="Hi!",
        model="openai/gpt-5",
        usage=UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        finish_reason="stop",
    )


class TestCodexAdapter:
    """Test CodexAdapter behavior and contract compliance."""

    async def test_requires_openai_api_key(self) -> None:
        """Returns provider-auth error when OPENAI_API_KEY is missing."""
        adapter = CodexAdapter()

        with patch.dict("os.environ", {}, clear=True):
            result = await adapter.complete(_sample_messages(), _sample_config())

        assert result.is_err
        assert result.error.provider == "codex"
        assert result.error.status_code == 401
        assert "OPENAI_API_KEY" in result.error.message

    async def test_passes_model_through_unchanged(self) -> None:
        """Delegates with original CompletionConfig model value unchanged."""
        adapter = CodexAdapter()
        messages = _sample_messages()
        config = CompletionConfig(model="openai/gpt-5-mini")

        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            with patch(
                "ouroboros.providers.litellm_adapter.LiteLLMAdapter.complete",
                new_callable=AsyncMock,
            ) as mock_complete:
                mock_complete.return_value = Result.ok(_sample_response())
                result = await adapter.complete(messages, config)

        assert result.is_ok
        _, call_config = mock_complete.await_args.args
        assert call_config.model == "openai/gpt-5-mini"

    async def test_normalizes_provider_errors_to_codex(self) -> None:
        """Maps expected provider errors to provider='codex'."""
        adapter = CodexAdapter()
        upstream_error = ProviderError(
            "Upstream failure",
            provider="openai",
            status_code=429,
            details={"original_exception": "RateLimitError"},
        )

        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            with patch(
                "ouroboros.providers.litellm_adapter.LiteLLMAdapter.complete",
                new_callable=AsyncMock,
            ) as mock_complete:
                mock_complete.return_value = Result.err(upstream_error)
                result = await adapter.complete(_sample_messages(), _sample_config())

        assert result.is_err
        assert result.error.provider == "codex"
        assert result.error.status_code == 429
        assert result.error.details["upstream_provider"] == "openai"

    async def test_maps_unexpected_delegate_exception(self) -> None:
        """Converts unexpected delegate exceptions to codex ProviderError."""
        adapter = CodexAdapter()

        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            with patch(
                "ouroboros.providers.litellm_adapter.LiteLLMAdapter.complete",
                new_callable=AsyncMock,
            ) as mock_complete:
                mock_complete.side_effect = RuntimeError("boom")
                result = await adapter.complete(_sample_messages(), _sample_config())

        assert result.is_err
        assert result.error.provider == "codex"
        assert "Unexpected error" in result.error.message

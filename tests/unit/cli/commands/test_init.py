"""Unit tests for ouroboros.cli.commands.init."""

import asyncio
from unittest.mock import patch

from ouroboros.providers.codex_adapter import CodexAdapter

from ouroboros.cli.commands.init import _get_adapter, _multiline_prompt_async, _safe_confirm


class TestSafeConfirm:
    """Test non-interactive confirmation handling."""

    def test_returns_confirm_result_when_interactive(self) -> None:
        """Returns normal Confirm.ask value when stdin is interactive."""
        with patch("ouroboros.cli.commands.init.Confirm.ask", return_value=True):
            assert _safe_confirm("Retry?", default=False) is True

    def test_uses_non_interactive_fallback_on_eof(self) -> None:
        """Falls back cleanly when Confirm.ask raises EOFError."""
        with patch("ouroboros.cli.commands.init.Confirm.ask", side_effect=EOFError):
            with patch("ouroboros.cli.commands.init.print_warning") as mock_warning:
                assert _safe_confirm("Retry?", default=True, non_interactive_default=False) is False
                assert mock_warning.called


class TestMultilinePrompt:
    """Test question input behavior in interactive and non-interactive modes."""

    def test_non_interactive_uses_plain_input(self) -> None:
        """Uses built-in input fallback when stdin is not a TTY."""
        with patch("sys.stdin.isatty", return_value=False):
            with patch("builtins.input", return_value="seed details"):
                result = asyncio.run(_multiline_prompt_async("Your response"))

        assert result == "seed details"

    def test_non_interactive_eof_raises_actionable_error(self) -> None:
        """Raises clear runtime error when non-interactive stdin has no input."""
        with patch("sys.stdin.isatty", return_value=False):
            with patch("builtins.input", side_effect=EOFError):
                try:
                    asyncio.run(_multiline_prompt_async("Your response"))
                    assert False, "Expected RuntimeError"
                except RuntimeError as exc:
                    assert "Non-interactive stdin has no interview response input" in str(exc)


class TestGetAdapter:
    """Test provider adapter selection for interviews."""

    def test_claude_mode_falls_back_to_codex_when_sdk_missing(self) -> None:
        """Claude mode degrades to Codex when Claude SDK is unavailable."""
        with patch("ouroboros.cli.commands.init.claude_agent_sdk_available", return_value=False):
            adapter = _get_adapter("claude_code")

        assert isinstance(adapter, CodexAdapter)

"""Unit tests for ouroboros.cli.commands.init."""

from unittest.mock import patch

from ouroboros.cli.commands.init import _safe_confirm


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

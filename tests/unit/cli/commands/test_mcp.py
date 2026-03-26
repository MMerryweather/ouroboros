"""Unit tests for ouroboros.cli.commands.mcp."""

from types import SimpleNamespace
from unittest.mock import patch

from ouroboros.cli.commands.mcp import _configure_stdio_runtime_safety


class TestConfigureStdioRuntimeSafety:
    """Test stdio MCP runtime hardening."""

    def test_disables_console_logging_and_litellm_noise(self) -> None:
        """Silences console logging and LiteLLM verbosity for stdio transport."""
        fake_litellm = SimpleNamespace(
            set_verbose=True,
            suppress_debug_info=False,
            turn_off_message_logging=False,
            json_logs=True,
        )

        with (
            patch("ouroboros.observability.logging.set_console_logging") as mock_set_console_logging,
            patch.dict("sys.modules", {"litellm": fake_litellm}),
        ):
            _configure_stdio_runtime_safety()

        mock_set_console_logging.assert_called_once_with(False)
        assert fake_litellm.set_verbose is False
        assert fake_litellm.suppress_debug_info is True
        assert fake_litellm.turn_off_message_logging is True
        assert fake_litellm.json_logs is False

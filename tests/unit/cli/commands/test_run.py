"""Unit tests for ouroboros.cli.commands.run."""

import pytest
import typer
from unittest.mock import patch

from ouroboros.cli.commands.run import _run_orchestrator


class TestRunOrchestrator:
    """Test orchestrator preflight behavior."""

    @pytest.mark.asyncio
    async def test_requires_claude_sdk_before_starting(self, tmp_path) -> None:
        """Orchestrator mode fails fast when the Claude SDK is unavailable."""
        seed_path = tmp_path / "seed.yaml"
        seed_path.write_text("goal: test\n", encoding="utf-8")

        with (
            patch("ouroboros.cli.commands.run.claude_agent_sdk_available", return_value=False),
            patch("ouroboros.cli.commands.run.print_error") as mock_error,
        ):
            with pytest.raises(typer.Exit) as exc_info:
                await _run_orchestrator(seed_path)

        assert exc_info.value.exit_code == 1
        mock_error.assert_called_once()
        assert "Claude Agent SDK is not installed" in mock_error.call_args.args[0]

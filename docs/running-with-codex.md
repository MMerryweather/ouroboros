# Running Ouroboros with Codex (Primary)

This is the canonical runtime path for Ouroboros.

<!-- PRIMARY_PATH_START -->
## Prerequisites

- Python 3.14+
- `uv`
- `OPENAI_API_KEY`

## Install and Configure

```bash
cd /path/to/ouroboros
uv sync
export OPENAI_API_KEY="your-openai-key"
```

## Validate Runtime

```bash
uv run ouroboros mcp info
```

Expected behavior:
- command exits `0`
- MCP server information is shown
- tool list includes `ouroboros_session_status`

## Codex Session Workflow

Open a Codex session at repository root and run:

```
ooo help
ooo interview "Build a tiny smoke-test CLI"
ooo seed
ooo run
ooo evaluate
```

Routing contract:
- `ooo <subcommand>` at message start has highest priority
- bare `ooo` routes to `welcome`
- trigger-keyword routing is used when no prefix route exists

## Notes

- Primary path does not require legacy plugin installation.
- `.claude-plugin/*` assets remain in the repository for legacy compatibility only.
<!-- PRIMARY_PATH_END -->

## Legacy Claude Compatibility

If you need Claude-specific setup, use:
[docs/running-with-claude-code.md](running-with-claude-code.md)

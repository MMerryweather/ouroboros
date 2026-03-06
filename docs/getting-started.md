# Getting Started with Ouroboros

Use this guide to run Ouroboros in a repository-local Codex session.

<!-- PRIMARY_PATH_START -->
## Primary Path: Codex-Native

### Prerequisites
- Python 3.14+
- `uv`
- `OPENAI_API_KEY` in your environment

### Setup
```bash
cd /path/to/ouroboros
uv sync
export OPENAI_API_KEY="your-openai-key"
```

### Run the workflow in a Codex session opened at this repo
```
ooo help
ooo interview "Build a task management CLI"
ooo seed
ooo run
ooo evaluate
```

### Verify MCP availability
```bash
uv run ouroboros mcp info
```

If `mcp info` lists tools such as `ouroboros_session_status`, setup is valid.

Canonical runtime guide: [running-with-codex.md](running-with-codex.md)
<!-- PRIMARY_PATH_END -->

## Legacy Claude Path (Optional)

Claude plugin/Max-plan workflows remain documented for compatibility only:
[running-with-claude-code.md](running-with-claude-code.md)

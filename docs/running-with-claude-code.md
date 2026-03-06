# Running Ouroboros with Claude Code (Legacy)

This document is kept for backward compatibility.
The primary supported path is Codex-native: [running-with-codex.md](running-with-codex.md).

<!-- LEGACY_CLAUDE_START -->
## Legacy Prerequisites

- Claude Code CLI installed and authenticated (Max Plan)
- Python 3.14+

## Legacy Install

```bash
pip install ouroboros-ai
# or
uv pip install ouroboros-ai
```

## Legacy Workflow

```bash
# Start interview using Claude Code orchestrator path
uv run ouroboros init start --orchestrator "Build a REST API for task management"

# Execute a seed using orchestrator mode
uv run ouroboros run workflow --orchestrator my-task.yaml
```

## Legacy Notes

- This path relies on Claude authentication/runtime.
- It is optional and non-primary.
- New onboarding should use `docs/running-with-codex.md`.
<!-- LEGACY_CLAUDE_END -->

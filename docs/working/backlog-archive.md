# Backlog Archive

## 2026-03-06

- Item: Port Ouroboros from Claude plugin packaging to native ChatGPT Codex workflow.
  - Original ExecPlan: docs/exec-plans/completed/20260306-port-claude-plugin-to-native-chatgpt-codex.md
  - Context: Make `ooo` workflow usable natively in Codex sessions without Claude marketplace/plugin runtime prerequisites.
  - Scope Delivered:
    - Codex provider adapter + config wiring (`CodexAdapter`, provider mode support).
    - Deterministic `ooo` routing precedence and tie-break behavior.
    - Codex-first documentation contract with primary/legacy markers.
    - Full artifact ladder for preflight, CP-1 integration, PR review, test-review, and final QA.
  - Acceptance Summary:
    - Primary docs route Codex-first and avoid requiring Claude installation in primary-path blocks.
    - Routing behavior and provider behavior covered by unit/integration tests.
    - MCP registration/probe and session-evidence artifacts captured.
  - Testing Summary:
    - Provider/config/routing/integration suites passed in recorded artifacts.
    - Final quality-gate artifacts (`ruff`, `mypy`, `pytest`, `mcp`, smoke evidence) captured under `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/`.

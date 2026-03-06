# Port Ouroboros From Claude Plugin Packaging to Native ChatGPT Codex Workflow

This ExecPlan is a living document maintained in accordance with `docs/PLANS.md`. The sections Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective must be kept up to date as work proceeds.

## Purpose / Big Picture

After this change, a developer can use Ouroboros natively in ChatGPT Codex-style sessions without relying on Claude Plugin marketplace installation (`claude plugin install ...`) or Claude-only command scaffolding. The user-visible outcome is that the same `ooo` workflow intent (interview, seed, run, evaluate, evolve, status, unstuck, ralph) is available through repository-native Codex instruction and runtime entrypoints, with documented setup and verification paths.

How to see it working after implementation:
1. In a Codex session opened at this repository, enter `ooo help` and receive routed help behavior from local skill docs.
2. Run the Codex-compatible setup flow and verify MCP server registration plus command routing without requiring `.claude-plugin/plugin.json` installation.
3. Execute one full workflow path (`ooo interview` -> `ooo seed` -> `ooo run`) and confirm expected artifacts/events are produced.

## Progress

- [x] (2026-03-06 13:28 UTC) Create preflight gate artifacts proving local runtime/tooling/auth prerequisites for Codex-native execution.
- [x] (2026-03-06 13:28 UTC) Produce a compatibility contract document mapping Claude plugin constructs to Codex-native constructs.
- [x] (2026-03-06 13:33 UTC) Implement provider/runtime abstraction changes for Codex-native execution path while preserving existing behavior.
- [x] (2026-03-06 13:40 UTC) Implement command routing and skill/agent loading changes for Codex-native invocation.
- [x] (2026-03-06 13:43 UTC) Update setup flow and documentation to make Codex-native path primary and Claude-plugin path optional/legacy.
- [x] (2026-03-06 13:46 UTC) Enforce Codex-only primary guardrail: primary workflow must run without `claude` binary or Claude plugin manifests.
- [x] (2026-03-06 13:46 UTC) Add and update unit/integration tests for new routing/provider/setup behavior.
- [x] (2026-03-06 13:46 UTC) Run integration checkpoints after each parallel batch and record required artifacts.
- [ ] Run PR-style review and apply fixes.
- [ ] Run in-session test-review checklist and record status artifact.
- [ ] Run fresh post-review quality gates on HEAD and record fresh evidence artifacts.
- [ ] Knowledge Harvest: classify each Surprise by issue class, encode durable fix into `AGENTS.md` or `docs/`, record in Outcomes & Retrospective > Knowledge Harvest.

Use timestamps when completing items, for example:
- [x] (2026-03-06 10:40 UTC) Compatibility contract finalized.

## Surprises & Discoveries

- Observation: PKG-0 preflight initially failed because `uv` was not installed and `uv run` dependency resolution failed under sandboxed network restrictions.
  Evidence: Initial preflight run exited non-zero with `uv: command not found` and subsequent `litellm` DNS fetch failures; elevated retry succeeded and `preflight-gate: PASS` was recorded in `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/preflight.txt`.

- Observation: `uv run ouroboros mcp info` initially failed in sandbox because the CLI attempted to create `~/.ouroboros/logs`, which is read-only in this execution context.
  Evidence: First MCP probe attempt raised `OSError: [Errno 30] Read-only file system: '/home/mat/.ouroboros'`; elevated retry succeeded and produced tool inventory in `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-probe.txt`.

- Observation: Directly extending `LiteLLMAdapter` preserved retry and request semantics, but provider labels from upstream errors required explicit normalization to satisfy the Codex contract.
  Evidence: Added `CodexAdapter` wrapper that rewrites all `Result.err` provider labels to `codex`; unit tests in `tests/unit/providers/test_codex_adapter.py` verify normalized provider mapping and auth gating.

- Observation: PKG-2 unit tests initially failed in sandboxed execution because registry imports initialize file logging under `~/.ouroboros/logs`, which is read-only in this context.
  Evidence: First `pytest tests/unit/plugin/skills/test_registry.py -v` run failed at collection with `OSError: [Errno 30] Read-only file system`; elevated retry passed and was recorded in `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-2-tests.txt`.

- Observation: Primary-path marker guardrails were absent from all required docs before PKG-3, so automated doc audits could not prove Codex-first guidance boundaries.
  Evidence: Added marker pairs to `README.md`, `docs/getting-started.md`, and `docs/running-with-codex.md`, plus legacy markers in `docs/running-with-claude-code.md`; audit results are in `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-3-doc-audit.txt`.

- Observation: CP-1 integration checkpoint initially failed in sandbox due read-only home logging paths; rerun in elevated context passed all selected suites.
  Evidence: First run failed with `OSError: [Errno 30] Read-only file system: '/home/mat/.ouroboros/logs/ouroboros.log'`; second run passed `113 passed` and was recorded in `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/checkpoint-1-integration.txt`.

- Observation: Codex-only guardrail initially failed due banned legacy phrase in a primary-path block, requiring a wording-only documentation correction.
  Evidence: Guardrail failure and pass retry are captured in `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-only-guardrail.txt` with `guardrail-pass: primary-path blocks are Codex-only`.

## Decision Log

- Decision: Treat this user request as the authoritative backlog source because `docs/working/backlog.md` and `docs/working/assistant_state.md` are absent in this repository.
  Rationale: Planning cannot block on non-existent backlog files; explicit user directive provides scope and intent.
  Date/Author: 2026-03-06 / Planning Agent

- Decision: Make Codex-only minimal path the required primary outcome; Claude assets are treated as legacy compatibility docs only and cannot be runtime prerequisites.
  Rationale: User requirement is explicit Codex-only execution with minimal dependency surface.
  Date/Author: 2026-03-06 / Planning Agent

- Decision: Follow repository’s existing error-handling and model patterns (`Result[T,E]`, frozen dataclasses, protocol-driven adapters) for new Codex runtime integration.
  Rationale: `docs/contributing/key-patterns.md` defines these as codebase invariants and they reduce integration risk.
  Date/Author: 2026-03-06 / Planning Agent

- Decision: Use Python/uv quality gates (`ruff`, `mypy`, `pytest`) instead of npm-based gates.
  Rationale: This repository is Python-first (`pyproject.toml`, `docs/contributing/testing-guide.md`, `.github/workflows/test.yml`).
  Date/Author: 2026-03-06 / Planning Agent

- Decision: Execute PKG-0 gate retries under elevated context after sandbox-only failures, and persist both failed and successful attempts in PKG-0 artifacts.
  Rationale: `docs/PLANS.md` guardrails require single-variable retry on execution context plus explicit evidence of both attempts when restrictions block validation.
  Date/Author: 2026-03-06 / Building Agent

- Decision: Implement Codex as a strict wrapper over `LiteLLMAdapter` instead of introducing a new SDK-specific adapter.
  Rationale: This preserves existing retry behavior and request construction while enforcing Codex-specific auth/error contracts (`OPENAI_API_KEY` requirement and `ProviderError(provider="codex")` normalization).
  Date/Author: 2026-03-06 / Building Agent

- Decision: Enforce deterministic skill routing in PKG-2 by applying contract-priority ordering and stable tie-break logic (longest match first, then lexical skill name).
  Rationale: Existing routing behavior depended on dictionary/set iteration order and confidence-only sorting, which could produce non-deterministic selection under multiple trigger matches.
  Date/Author: 2026-03-06 / Building Agent

- Decision: Make `docs/running-with-codex.md` the canonical runtime guide and reduce Claude-specific instructions to explicitly labeled legacy compatibility docs.
  Rationale: PKG-3 contract requires Codex-native as primary with marker-scoped guardrails and optional Claude path only.
  Date/Author: 2026-03-06 / Building Agent

- Decision: Complete CP-1 in PKG-4 by rerunning checkpoint tests in elevated context after sandbox-only filesystem failures, and record both attempts in checkpoint artifacts.
  Rationale: CP-1 evidence must be boundary-true and non-empty; sandbox restrictions are execution-context issues rather than code regressions.
  Date/Author: 2026-03-06 / Building Agent

- Decision: Apply a minimal wording fix in `docs/running-with-codex.md` to remove banned legacy install phrasing from a primary-path marker block.
  Rationale: Codex-only guardrail intentionally fails on legacy install strings in primary blocks; this fix was the minimum change to satisfy contract enforcement.
  Date/Author: 2026-03-06 / Building Agent

## Outcomes & Retrospective

(Filled in at completion.)

### Knowledge Harvest

(Completed just before PR, after implementation; see `docs/PLANS.md` guidance.)

- Class: [type of recurring issue].
  Fix: [rule or guardrail added].
  Encoded in: [file/section].

## Definition of Done

Before marking this exec plan complete, verify:
- [ ] All Progress checklist items are complete.
- [ ] Tests exist for new/changed behavior.
- [ ] Post-review quality gates pass with fresh evidence.
- [ ] Documentation updates are complete.
- [ ] Test-review phase is complete and artifact recorded.
- [ ] Knowledge Harvest is complete and encoded in docs/AGENTS.
- [ ] Codex-native workflow demonstration succeeds without requiring Claude marketplace plugin install.
- [ ] Codex-native workflow demonstration succeeds when `claude` binary is unavailable.

## Context and Orientation

Ouroboros currently exposes two overlapping surfaces:
1. Python runtime and orchestration engine (`src/ouroboros/**`) driven by Typer CLI and MCP server.
2. Claude plugin packaging (`.claude-plugin/`, `skills/`, `commands/`, root `AGENTS.md` guidance) that routes `ooo` commands inside Claude Code.

The port focuses on making Codex-native execution the first-class path while preserving the same user intent and workflow stages.

Key files in this repository:
- `AGENTS.md`: Local command-routing contract for `ooo` commands and skill file mapping.
- `.claude-plugin/plugin.json`: Legacy Claude plugin manifest (documented, non-primary).
- `.claude-plugin/.mcp.json`: Legacy Claude plugin MCP payload (non-primary).
- `skills/*/SKILL.md`: Command-specific behavior definitions (interview/seed/run/evaluate/etc.).
- `commands/*.md`: Thin command wrappers that delegate to skill docs.
- `src/ouroboros/plugin/skills/registry.py`: Discovery and indexing for skill metadata.
- `src/ouroboros/plugin/skills/keywords.py`: Magic prefix and keyword detection (`ooo`, `ouroboros:`).
- `src/ouroboros/plugin/agents/registry.py`: Built-in and custom agent registration.
- `src/ouroboros/providers/base.py`: Provider protocol (`LLMAdapter`) and message/completion models.
- `src/ouroboros/providers/claude_code_adapter.py`: Claude Agent SDK-backed provider.
- `src/ouroboros/cli/commands/mcp.py`: MCP server runtime entrypoint.
- `docs/getting-started.md` and `docs/running-with-claude-code.md`: User setup docs that currently center Claude plugin paths.
- `tests/unit/plugin/**`, `tests/integration/plugin/**`: Existing plugin behavior test coverage.

Merge-conflict hotspots (high shared-edit risk):
- `AGENTS.md` (root command contract).
- `README.md` and `docs/getting-started.md` (installation narrative).
- `src/ouroboros/plugin/skills/keywords.py` (cross-cutting command routing).
- `src/ouroboros/providers/__init__.py` (provider import/export hub).

Terms defined:
- **Codex-native**: Running from ChatGPT Codex environment using repository-local instructions/tools, without Claude plugin marketplace packaging.
- **Primary path**: The default user flow documented and tested as required. In this plan, primary path means Codex-only and must not depend on Claude binaries or Claude plugin manifests.
- **MCP (Model Context Protocol)**: A protocol that lets the assistant call structured tools/resources; here served by `ouroboros mcp serve`.
- **Skill**: A markdown instruction file (`skills/<name>/SKILL.md`) describing how a command should behave.
- **Provider adapter**: A Python class implementing `LLMAdapter` to talk to a model runtime.
- **Preflight gate**: Initial verification milestone that checks prerequisites before implementation or end-to-end validation.
- **Evidence artifact**: Saved output/log file proving a step passed or failed.

Non-goals for this plan:
- Do not add new Claude-specific runtime features.
- Do not require edits to `.claude-plugin/*` for Codex primary-path success.
- Do not increase setup complexity beyond minimal Codex + repository prerequisites.

## Plan of Work

The implementation proceeds in five major milestones with mandatory checkpointing.

### Binding Contracts (Must Be Implemented Exactly)

Codex adapter contract (binding for PKG-1):
- Backend/library: `CodexAdapter` is a thin adapter over existing `LiteLLMAdapter` (`litellm.acompletion`) to avoid introducing a new SDK dependency.
- Auth source: `OPENAI_API_KEY` is required for Codex primary path. Missing key must return `Result.err(ProviderError(...))` with actionable remediation text.
- Model mapping: `CompletionConfig.model` passes through unchanged; no hidden model rewrite in adapter. Tier selection remains in existing routing/config layers.
- Retry behavior: reuse retry policy semantics from `LiteLLMAdapter` (`stamina` + existing retriable exception set) so behavior is deterministic.
- Error mapping: all expected runtime failures must map to `ProviderError` with provider tag `codex`; no raw exceptions from adapter for expected failures.
- Fallback behavior: no fallback to Claude runtime in Codex primary path. Claude adapter may remain installed but is never implicitly selected.

Codex command-routing contract (binding for PKG-2):
- `ooo <subcommand>` at message start takes precedence.
- Bare `ooo` routes to `welcome`.
- Trigger-keyword matching applies only when no command-prefix match exists.
- Tie-breaker is deterministic: longest match first, then lexical skill name.

Codex documentation contract (binding for PKG-3):
- `docs/running-with-codex.md` is canonical.
- Primary-path docs (`README.md`, `docs/getting-started.md`, `docs/running-with-codex.md`) must not require Claude installation.
- Legacy mentions are allowed only in explicitly labeled legacy sections.

Milestone A establishes non-negotiable execution contracts before code edits. It captures Codex runtime/tooling assumptions, available command surfaces, and auth/token sourcing in a written compatibility contract. If this contract cannot be validated, the plan must stop as blocked.

Milestone B implements runtime abstractions: add Codex-capable provider adapter(s), configuration wiring, and provider selection logic while preserving existing providers as optional non-primary paths.

Milestone C implements command-surface migration: Codex-first routing for `ooo` commands and skill/agent loading behavior with explicit trigger precedence and deterministic tie-breaking.

Milestone D updates documentation and packaging surfaces so new users follow Codex-native onboarding by default, and Claude plugin assets are explicitly documented as legacy and not required for runtime.

Milestone E adds/updates tests, runs review + test-review + post-review quality gates, and captures fresh evidence from HEAD.

### Milestone A: Preflight and Compatibility Contract (Gate)

Scope: validate critical dependencies and remove unknowns before build work.

Detailed steps:
1. Create artifact workspace ` .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/ `.
   - Purpose: single place for all required evidence.
2. Run tooling/runtime preflight checks.
   - Validate Python/uv toolchain, repository importability, and CLI presence.
   - Validate Codex execution context assumptions (environment variables, available tools, command routing entrypoint).
3. Produce `codex-compat-contract.md` artifact with explicit mappings:
   - Claude plugin construct -> Codex-native construct.
   - Identity/credential source for each validation step.
   - Unsupported features and mitigation.
4. Enforce evidence ladder for Codex-native integration:
   - Identity/auth check: confirm runtime identity and available auth source.
   - Permission check: confirm required tool execution permissions exist.
   - Dry-run operation: execute non-mutating command-path validation (`ooo help`).
   - Real operation: execute one minimal mutating workflow action (`ooo interview ...`) and verify output artifact/event.
5. Gate rule:
   - If any critical contract remains unknown (command routing, provider execution, MCP invocation path), stop and emit blocked status in artifact and plan notes.

### Milestone B: Runtime Provider Port

Scope: introduce Codex-native provider path and keep existing providers intact.

Detailed steps:
1. Create `src/ouroboros/providers/codex_adapter.py`.
   - Purpose: `LLMAdapter` implementation for Codex-native execution path.
   - Pattern to follow: `src/ouroboros/providers/claude_code_adapter.py` and `src/ouroboros/providers/litellm_adapter.py`.
2. Update provider exports/import hubs (for example `src/ouroboros/providers/__init__.py`).
3. Update configuration model/loader to support selecting Codex provider mode where provider choice is currently Claude/LiteLLM-only.
4. Add unit tests for adapter behavior and failure mapping (Result semantics, retry behavior, error normalization).

### Milestone C: Command Routing and Skill Surface Port

Scope: make `ooo` command behavior first-class in Codex-native sessions.

Detailed steps:
1. Update routing logic in `src/ouroboros/plugin/skills/keywords.py` and related registries with fixed precedence:
   - Priority 1: exact `ooo <subcommand>` at message start.
   - Priority 2: bare `ooo` -> `welcome`.
   - Priority 3: natural-language trigger keywords.
   - Tie-breaker: longest exact match, then lexical order of skill name.
2. Update execution pathway in `src/ouroboros/plugin/skills/executor.py` and `src/ouroboros/plugin/skills/registry.py` to remove Claude-only assumptions in primary path.
3. Ensure agent loading in `src/ouroboros/plugin/agents/registry.py` remains deterministic and testable.
4. Add routing tests proving precedence and tie-break behavior for Codex-triggered inputs.

### Milestone D: Documentation and Distribution Contract

Scope: align user-facing docs and repo metadata with Codex-native primary path.

Detailed steps:
1. Create `docs/running-with-codex.md` as the canonical runtime guide and link it from `README.md` and `docs/getting-started.md`.
2. Update `AGENTS.md` command contract to reflect Codex-native usage expectations.
3. Keep `.claude-plugin/*` files unchanged for historical compatibility, but mark them in docs as legacy/non-primary and non-required for execution.
4. Add explicit section markers in primary docs:
   - `<!-- PRIMARY_PATH_START -->` / `<!-- PRIMARY_PATH_END -->`
   - `<!-- LEGACY_CLAUDE_START -->` / `<!-- LEGACY_CLAUDE_END -->`
   These markers are mandatory for guardrail automation.
5. Document migration matrix and rollback instructions.

### Milestone E: Validation, Review, and Final Gates

Scope: prove end-to-end behavior and quality after review fixes.

Detailed steps:
1. Run targeted unit/integration suites for provider + plugin routing changes.
2. Run a manual Codex-native workflow smoke test and capture transcript.
3. Execute PR-style review pass, apply fixes, and rerun affected tests.
4. Execute mandatory test-review checklist pass; write structured status artifact.
5. Run fresh post-review quality gates on HEAD with fresh artifact logs.
6. Confirm all Definition of Done items and complete Knowledge Harvest.

## Parallel Work Packages

### Package Definitions

- **ID**: PKG-0
  - **Goal**: Produce preflight and compatibility contract artifacts that unblock all build work.
  - **Owned paths**: `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/preflight.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-adapter-contract.md`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-compat-contract.md`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-registration-check.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-probe.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-tool-call-proof.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-identity.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-permission.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-dry-run.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-real-op.txt`
  - **Depends on**: none
  - **Parallel-safe with**: none (gate package)
  - **Validation**: preflight command block in Concrete Steps
  - **Artifacts**: `preflight.txt`, `codex-adapter-contract.md`, `codex-compat-contract.md`, `mcp-registration-check.txt`, `mcp-probe.txt`, `mcp-tool-call-proof.txt`, `evidence-identity.txt`, `evidence-permission.txt`, `evidence-dry-run.txt`, `evidence-real-op.txt`

- **ID**: PKG-1
  - **Goal**: Implement Codex provider adapter and provider-selection wiring.
  - **Owned paths**: `src/ouroboros/providers/codex_adapter.py`, `src/ouroboros/providers/__init__.py`, `src/ouroboros/config/models.py`, `src/ouroboros/config/loader.py`
  - **Depends on**: PKG-0
  - **Parallel-safe with**: PKG-2, PKG-3
  - **Validation**: provider unit tests + mypy for provider/config modules
  - **Artifacts**: `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-1-tests.txt`

- **ID**: PKG-2
  - **Goal**: Port skill/keyword routing for Codex-native command behavior.
  - **Owned paths**: `src/ouroboros/plugin/skills/keywords.py`, `src/ouroboros/plugin/skills/registry.py`, `src/ouroboros/plugin/skills/executor.py`, `tests/unit/plugin/skills/test_registry.py`
  - **Depends on**: PKG-0
  - **Parallel-safe with**: PKG-1, PKG-3
  - **Validation**: plugin skill/routing unit tests
  - **Artifacts**: `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-2-tests.txt`

- **ID**: PKG-3
  - **Goal**: Update docs/setup/distribution contract to Codex-native primary path.
  - **Owned paths**: `README.md`, `docs/getting-started.md`, `docs/running-with-codex.md`, `docs/running-with-claude-code.md`, `AGENTS.md`
  - **Depends on**: PKG-0
  - **Parallel-safe with**: PKG-1, PKG-2 (except hotspot merge checkpoint required)
  - **Validation**: docs consistency grep + setup docs smoke transcript
  - **Artifacts**: `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-3-doc-audit.txt`

- **ID**: PKG-4
  - **Goal**: Integration and QA recomposition after parallel batches; enforce review + test-review + post-review gates.
  - **Owned paths**: `tests/integration/plugin/test_orchestration.py`, `tests/integration/test_entry_point.py`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/run-context.sh`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/checkpoint-1-integration.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-test-review.md`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-check.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-format-check.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mypy.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-pytest.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-smoke-codex.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-probe.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-tool-call-proof.txt`, `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-only-guardrail.txt`
  - **Depends on**: PKG-1, PKG-2, PKG-3
  - **Parallel-safe with**: none
  - **Validation**: integration tests + final quality gates
  - **Artifacts**: `run-context.sh`, `checkpoint-1-integration.txt`, `codex-only-guardrail.txt`, `final-test-review.md`, `final-ruff-check.txt`, `final-ruff-format-check.txt`, `final-mypy.txt`, `final-pytest.txt`, `final-smoke-codex.txt`, `final-mcp-probe.txt`, `final-mcp-tool-call-proof.txt`

### Ownership Matrix

- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/preflight.txt` -> `PKG-0`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-adapter-contract.md` -> `PKG-0`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-compat-contract.md` -> `PKG-0`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-registration-check.txt` -> `PKG-0`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-probe.txt` -> `PKG-0`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-tool-call-proof.txt` -> `PKG-0`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-identity.txt` -> `PKG-0`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-permission.txt` -> `PKG-0`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-dry-run.txt` -> `PKG-0`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-real-op.txt` -> `PKG-0`
- `src/ouroboros/providers/codex_adapter.py` -> `PKG-1`
- `src/ouroboros/providers/__init__.py` -> `PKG-1`
- `src/ouroboros/config/models.py` -> `PKG-1`
- `src/ouroboros/config/loader.py` -> `PKG-1`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-1-tests.txt` -> `PKG-1`
- `src/ouroboros/plugin/skills/keywords.py` -> `PKG-2`
- `src/ouroboros/plugin/skills/registry.py` -> `PKG-2`
- `src/ouroboros/plugin/skills/executor.py` -> `PKG-2`
- `tests/unit/plugin/skills/test_registry.py` -> `PKG-2`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-2-tests.txt` -> `PKG-2`
- `README.md` -> `PKG-3`
- `docs/getting-started.md` -> `PKG-3`
- `docs/running-with-codex.md` -> `PKG-3`
- `docs/running-with-claude-code.md` -> `PKG-3`
- `AGENTS.md` -> `PKG-3`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-3-doc-audit.txt` -> `PKG-3`
- `tests/integration/plugin/test_orchestration.py` -> `PKG-4`
- `tests/integration/test_entry_point.py` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/run-context.sh` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/checkpoint-1-integration.txt` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-test-review.md` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-check.txt` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-format-check.txt` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mypy.txt` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-pytest.txt` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-smoke-codex.txt` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-probe.txt` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-tool-call-proof.txt` -> `PKG-4`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-only-guardrail.txt` -> `PKG-4`

Hotspot file integration sequence:
1. Merge PKG-1 first (non-hotspot provider/config files).
2. Merge PKG-3 second (`AGENTS.md` and primary docs).
3. Merge PKG-2 third (`src/ouroboros/plugin/skills/keywords.py` and routing code).
4. Run CP-1 checkpoint tests immediately after merge sequence.

## Execution DAG and Critical Path

Dependency edges:
- PKG-1 depends on PKG-0.
- PKG-2 depends on PKG-0.
- PKG-3 depends on PKG-0.
- PKG-4 depends on PKG-1, PKG-2, PKG-3.

Execution batches:
- Batch 0 (sequential gate): PKG-0.
- Batch 1 (parallel): PKG-1, PKG-2, PKG-3.
- Batch 2 (sequential integration): PKG-4.

Critical path:
- `PKG-0 -> PKG-2 -> PKG-4` (routing changes are highest risk for end-to-end command behavior).

Sequential-only packages:
- PKG-0, PKG-4.

## Integration Checkpoints

### Checkpoint CP-0 (after PKG-0)

Required actions:
1. Validate `codex-adapter-contract.md` and `codex-compat-contract.md` contain concrete values (no unresolved placeholders/tokens).
2. Validate MCP registration and probe artifacts exist and show pass markers.
3. Validate Codex-session MCP tool-call proof artifact exists.
4. Validate auth proof exists via either `openai-api-key-present` marker or `provider-auth-success` marker.
5. Confirm no critical dependency is marked unknown.

Required artifacts:
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/preflight.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-adapter-contract.md`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-compat-contract.md`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-registration-check.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-probe.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-tool-call-proof.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-identity.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-permission.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-dry-run.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-real-op.txt`

Exit rule:
- If unresolved critical dependency exists, unresolved-token gate fails, auth proof is missing, MCP artifacts are missing, or MCP tool-call proof marker is missing, stop with blocked status. Do not start PKG-1/2/3.

### Checkpoint CP-1 (after Batch 1 merge)

Required actions:
1. Merge in canonical order: PKG-1 -> PKG-3 -> PKG-2.
2. Run contract tests for provider selection and skill routing.
3. Run docs consistency smoke checks.
4. Validate package-local artifacts exist: `pkg-1-tests.txt`, `pkg-2-tests.txt`, `pkg-3-doc-audit.txt`.
5. PKG-4 records the checkpoint result artifact before continuing to final QA steps.

Required artifacts:
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-1-tests.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-2-tests.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-3-doc-audit.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/checkpoint-1-integration.txt`

Exit rule:
- Any failing contract/smoke check blocks PKG-4.

### Checkpoint FINAL-QA (sequential, pre-PR)

Inputs:
- Current HEAD after PR-style review fixes.

Required actions:
1. Run test-review checklist pass in-session and record status.
2. Run fresh local quality gates on HEAD:
   - `uv run ruff check src tests`
   - `uv run ruff format --check src tests`
   - `uv run mypy src/ouroboros --ignore-missing-imports`
   - `uv run pytest tests/ -v -k "not test_run_workflow_verbose"`
3. Run Codex-native manual smoke flow and record transcript.
4. Re-run MCP probe and capture fresh artifact on current HEAD.
5. Re-run one Codex-session MCP tool call and capture fresh proof artifact.

Required artifacts:
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-test-review.md`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-check.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-format-check.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mypy.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-pytest.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-smoke-codex.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-probe.txt`
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-tool-call-proof.txt`

Exit rule:
- PR creation is blocked unless all required checks are green or explicitly deferred with rationale and a tracked follow-up ticket.

## Concrete Steps

All commands run from repository root `/home/mat/Documents/ouroboros` unless noted.
Execution context defaults:
- Context: host machine shell session in repository root.
- Identity source: local OS user session; no external token unless explicitly stated.
- Shell: `bash` (required for `set -euo pipefail` and `PIPESTATUS` semantics).

1. Preflight gate and contract creation.

    set -euo pipefail
    mkdir -p .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex
    {
      echo "# Preflight $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo "## Toolchain"
      python3 --version
      uv --version
      uv run python -V
      uv run python -c "import sys; assert sys.version_info >= (3, 14), sys.version; print('python-3.14+-ok')"
      echo "## Repo checks"
      test -f AGENTS.md && echo "AGENTS.md present"
      test -f docs/PLANS.md && echo "PLANS.md present"
      echo "## Candidate runtime"
      command -v codex >/dev/null && echo "codex command found" || echo "codex command not found (diagnostic only)"
      echo "## Codex-only guardrail"
      command -v claude >/dev/null && echo "claude binary present (must remain optional only)" || echo "claude binary absent (acceptable)"
    } | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/preflight.txt

Expected observations:
- Command exits 0 when Python 3.14+ gate passes.
- `preflight.txt` exists and includes toolchain versions.
- Guardrail line states Claude is optional and not required.

2. Write binding contract artifacts and enforce no-placeholder gate.

    cat > .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-adapter-contract.md <<'ADAPTER'
    # Codex Adapter Contract
    backend_library: LiteLLMAdapter
    transport: litellm.acompletion
    required_auth_env: OPENAI_API_KEY
    model_mapping: passthrough_completion_config_model
    retry_policy: stamina_retries_same_as_litellm_adapter
    expected_error_type: ProviderError(provider="codex")
    fallback_to_claude: forbidden_on_primary_path
    ADAPTER

    cat > .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-compat-contract.md <<'CONTRACT'
    # Codex Compatibility Contract

    runtime_command_surface: AGENTS.md + skills/*/SKILL.md command routing in Codex session
    invocation_context: Codex session for chat commands, bash shell for repository commands
    identity_token_source: OPENAI_API_KEY for CodexAdapter, local OS user for filesystem
    claude_plugin_manifest_role: legacy_only_non_runtime
    legacy_claude_mcp_path_role: legacy_only_non_runtime
    unsupported_or_deferred: none
    gate_status: PASS
    gate_reason: all critical contracts resolved
    CONTRACT

    if rg -n '\\[resolved value\\]|PASS\\|BLOCKED|\\[text\\]|\\[host/CI/container\\]|\\[Codex-native equivalent\\]' \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-adapter-contract.md \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-compat-contract.md; then
      echo "contract-placeholder-gate-fail" >&2
      exit 2
    fi
    if rg -ni 'unknown|tbd|todo|defer|\\[[^]]+\\]' \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-adapter-contract.md \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-compat-contract.md; then
      echo "contract-unresolved-token-gate-fail" >&2
      exit 2
    fi

Expected observations:
- Both contract files exist and contain concrete values (no placeholders).
- Placeholder gate command exits 0.
- Unresolved-token gate command exits 0.
- `codex-compat-contract.md` has `gate_status: PASS` before build milestones begin.

3. Evidence ladder execution (must run in order; stop at first failure).

    # Identity/auth check (context: host shell; identity: local session + configured provider credentials)
    set -euo pipefail
    {
      env | rg -i 'OPENAI|ANTHROPIC|OUROBOROS|CODEX' || true
      if [ -z "${OPENAI_API_KEY:-}" ]; then
        echo "openai-api-key-missing"
      else
        echo "openai-api-key-present"
      fi
    } | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-identity.txt

    # Permission check (context: host shell; identity: local session)
    test -r AGENTS.md && test -r skills/help/SKILL.md && echo \"read-permissions-ok\" | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-permission.txt

    # Dry run (context: Codex-native chat session bound to repo; identity: Codex session identity)
    # Execute: ooo help
    # Save transcript manually to:
    # .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-dry-run.txt

    # Real operation (same context/identity as dry run)
    # Execute: ooo interview \"Build a tiny smoke-test CLI\"
    # Append marker to transcript on success: provider-auth-success
    # Save transcript manually to:
    # .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-real-op.txt
    if ! rg -q 'openai-api-key-present' .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-identity.txt \
      && ! rg -q 'provider-auth-success' .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/evidence-real-op.txt; then
      uv run python - <<'PY'
from pathlib import Path
p = Path(".artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-compat-contract.md")
t = p.read_text()
t = t.replace("gate_status: PASS", "gate_status: BLOCKED")
t = t.replace("gate_reason: all critical contracts resolved", "gate_reason: missing auth proof (env key or provider-auth-success)")
p.write_text(t)
print("gate-status-updated-to-blocked")
PY
      exit 4
    fi

Expected observations:
- Identity artifact shows runtime/auth signals and explicit key-presence result.
- CP-0 auth proof must include either `openai-api-key-present` in identity artifact or `provider-auth-success` in real-op artifact.
- Permission artifact contains `read-permissions-ok`.
- Dry-run and real-op transcript artifacts exist; real-op demonstrates progression beyond help output.
- Dry-run and real-op evidence shows no dependency on `claude` command availability.
- Missing env key is acceptable only when provider auth is proven by `provider-auth-success` marker.

4. MCP registration and probe validation (Codex-primary path).

    set -euo pipefail
    uv run python - <<'PY' | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-registration-check.txt
import json, pathlib
p = pathlib.Path(".mcp.json")
if not p.exists():
    raise SystemExit("missing .mcp.json")
cfg = json.loads(p.read_text())
servers = cfg.get("mcpServers", {})
if "ouroboros" not in servers:
    raise SystemExit("missing mcpServers.ouroboros")
print("mcp-registration-ok")
PY
    uv run ouroboros mcp info | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-probe.txt
    # In Codex session context (with `.mcp.json` loaded), invoke one Ouroboros MCP tool:
    #   ouroboros_session_status
    # Append marker to transcript on success: mcp-tool-call-success
    # Save transcript/output to:
    # .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-tool-call-proof.txt
    rg -q 'mcp-tool-call-success' .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-tool-call-proof.txt
    rg -qi 'ouroboros_session_status|session_status' .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/mcp-tool-call-proof.txt

Expected observations:
- `mcp-registration-check.txt` contains `mcp-registration-ok`.
- `mcp-probe.txt` lists MCP server information and at least one tool.
- `mcp-tool-call-proof.txt` shows one successful Codex-session MCP tool invocation.
- Marker validation command exits 0.
- MCP transcript includes expected tool name/reference.
- All commands exit 0.

5. Implement PKG-1/PKG-2/PKG-3 in parallel using separate worktrees (one per child agent) from the same base SHA.

    set -euo pipefail
    RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
    BASE_SHA=$(git rev-parse HEAD)
    PKG1_WT="/tmp/ouroboros-pkg1-${RUN_ID}"
    PKG2_WT="/tmp/ouroboros-pkg2-${RUN_ID}"
    PKG3_WT="/tmp/ouroboros-pkg3-${RUN_ID}"
    git worktree add -b "feat/codex-provider-${RUN_ID}" "${PKG1_WT}" "$BASE_SHA"
    git worktree add -b "feat/codex-routing-${RUN_ID}" "${PKG2_WT}" "$BASE_SHA"
    git worktree add -b "feat/codex-docs-${RUN_ID}" "${PKG3_WT}" "$BASE_SHA"
    cat > .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/run-context.sh <<CTX
RUN_ID=${RUN_ID}
PKG1_WT=${PKG1_WT}
PKG2_WT=${PKG2_WT}
PKG3_WT=${PKG3_WT}
CTX
    # Assign one child agent per worktree and package ownership.
    # Canonical merge order after completion: PKG-1 -> PKG-3 -> PKG-2, then run CP-1.

Expected observations:
- Each package edits only owned paths.
- No overlapping ownership violations during merge.
- Merge sequence follows declared canonical order from same base SHA.
- Re-running creates new unique worktree/branch names via `RUN_ID` (idempotent retry).
- `run-context.sh` exists and can be sourced by later steps.

6. Package-local validation artifacts (must be produced before CP-1 merge checkpoint).

    set -euo pipefail
    REPO_ROOT="/home/mat/Documents/ouroboros"
    source .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/run-context.sh
    (cd "${PKG1_WT}" && uv run pytest tests/unit/providers -v) \
      | tee "${REPO_ROOT}/.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-1-tests.txt"
    (cd "${PKG2_WT}" && uv run pytest tests/unit/plugin/skills/test_registry.py -v) \
      | tee "${REPO_ROOT}/.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-2-tests.txt"
    {
      rg -n "<!-- PRIMARY_PATH_START -->|<!-- PRIMARY_PATH_END -->" "${PKG3_WT}/README.md" "${PKG3_WT}/docs/getting-started.md" "${PKG3_WT}/docs/running-with-codex.md"
      rg -n "<!-- LEGACY_CLAUDE_START -->|<!-- LEGACY_CLAUDE_END -->" "${PKG3_WT}/docs/running-with-claude-code.md"
    } | tee "${REPO_ROOT}/.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-3-doc-audit.txt"

Expected observations:
- `pkg-1-tests.txt` exists and provider unit tests pass.
- `pkg-2-tests.txt` exists and routing unit tests pass.
- `pkg-3-doc-audit.txt` exists and contains required primary/legacy markers.

7. Checkpoint CP-1 integration tests.

    set -euo pipefail
    uv run pytest tests/unit/providers tests/unit/plugin/skills tests/integration/plugin/test_orchestration.py tests/integration/test_entry_point.py -v | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/checkpoint-1-integration.txt
    uv run python - <<'PY' | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-only-guardrail.txt
from pathlib import Path
import re

primary_files = [
    Path("README.md"),
    Path("docs/getting-started.md"),
    Path("docs/running-with-codex.md"),
]
banned = re.compile(r"claude plugin install|~/.claude/mcp.json", re.IGNORECASE)

def extract_block(text: str, start: str, end: str) -> str:
    i = text.find(start)
    j = text.find(end)
    if i == -1 or j == -1 or j <= i:
        raise SystemExit(f"missing primary markers: {start} ... {end}")
    return text[i + len(start):j]

violations = []
for path in primary_files:
    text = path.read_text()
    block = extract_block(text, "<!-- PRIMARY_PATH_START -->", "<!-- PRIMARY_PATH_END -->")
    if banned.search(block):
        violations.append(str(path))

if violations:
    print("guardrail-fail: Claude requirement found in PRIMARY_PATH blocks")
    for v in violations:
        print(v)
    raise SystemExit(3)

print("guardrail-pass: primary-path blocks are Codex-only")
PY
    for f in \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-1-tests.txt \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-2-tests.txt \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/pkg-3-doc-audit.txt \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/checkpoint-1-integration.txt \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/codex-only-guardrail.txt; do
      test -s "$f"
    done

Expected observations:
- Exit code 0.
- Output includes passing status for provider and routing tests.
- Artifact file contains test summary line with all selected tests passing.
- `codex-only-guardrail.txt` contains `guardrail-pass` and verifies marker-based primary-path blocks only.
- Required CP-1 artifacts are non-empty (`test -s` checks pass).

8. PR-style review pass and fix cycle (before final gates).

    # Run review against current branch using in-session review process.
    # Apply fixes, then rerun targeted tests for touched areas.

Expected observations:
- Review findings are either fixed or explicitly deferred with rationale.
- No unresolved critical findings before final gate.

9. Mandatory test-review artifact creation.

    cat > .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-test-review.md <<'REVIEW'
    # Test Review Checklist
    - scope_coverage: pass|needs-attention|unknown
    - regression_risk: pass|needs-attention|unknown
    - flaky_test_risk: pass|needs-attention|unknown
    - interface_contracts: pass|needs-attention|unknown
    - migration_or_setup_impacts: pass|needs-attention|unknown

    ## Notes
    - [Required rationale for each non-pass item]
    REVIEW

Expected observations:
- Artifact exists.
- Any `needs-attention` item includes explicit rationale and follow-up ticket/reference.

10. Fresh post-review quality gates on HEAD.

    set -euo pipefail
    uv run ruff check src tests | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-check.txt
    uv run ruff format --check src tests | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-format-check.txt
    uv run mypy src/ouroboros --ignore-missing-imports | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mypy.txt
    uv run pytest tests/ -v -k "not test_run_workflow_verbose" | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-pytest.txt
    uv run ouroboros mcp info | tee .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-probe.txt
    # In Codex session context, re-run one Ouroboros MCP tool invocation and capture:
    # Append marker to transcript on success: mcp-tool-call-success
    # .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-tool-call-proof.txt
    rg -q 'mcp-tool-call-success' .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-tool-call-proof.txt
    rg -qi 'ouroboros_session_status|session_status' .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-tool-call-proof.txt
    for f in \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-test-review.md \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-check.txt \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-ruff-format-check.txt \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mypy.txt \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-pytest.txt \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-probe.txt \
      .artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/final-mcp-tool-call-proof.txt; do
      test -s "$f"
    done

Expected observations:
- Each command exits 0.
- Each artifact exists and contains pass indicators.
- Test output explicitly excludes only known pre-existing failing test.
- MCP probe output is present in `final-mcp-probe.txt`.
- Final Codex-session MCP invocation proof is present in `final-mcp-tool-call-proof.txt`.
- Final MCP marker validation command exits 0.
- Final MCP transcript includes expected tool name/reference.
- Required FINAL-QA artifacts are non-empty (`test -s` checks pass).

11. Boundary-true Codex smoke validation.

    # In Codex-native session context, run:
    #   ooo help
    #   ooo interview "Build a tiny sample"
    # Capture transcript into final-smoke-codex.txt

Expected observations:
- Commands resolve through Codex-native path (not Claude marketplace install requirement).
- Output confirms command routing and at least one workflow stage works.

## Validation and Acceptance

### Automated Tests

Run and pass:
- `uv run pytest tests/unit/providers tests/unit/plugin/skills tests/integration/plugin/test_orchestration.py tests/integration/test_entry_point.py -v`
- `uv run ruff check src tests`
- `uv run ruff format --check src tests`
- `uv run mypy src/ouroboros --ignore-missing-imports`
- `uv run pytest tests/ -v -k "not test_run_workflow_verbose"` (post-review fresh run)
- `uv run ouroboros mcp info` (must list server capabilities/tools)

Acceptance behavior:
- Provider layer selects Codex-compatible adapter when configured.
- `ooo` command routes correctly in Codex-native environment.
- Setup/docs no longer require Claude plugin marketplace as primary path.
- Primary-path commands succeed even when `claude` binary is absent.
- MCP server metadata and tool list are discoverable in Codex-primary configuration.
- At least one Ouroboros MCP tool call succeeds from Codex session and is captured as evidence.

### Manual Verification

1. Start a Codex session rooted at this repository.
2. Execute `ooo help`.
3. Execute `ooo interview "Build a small CLI"`.
4. Observe command routing succeeds and skill instructions are followed.
5. Confirm documentation steps match what was required in practice.
6. Verify primary flow does not invoke `claude` CLI or require `.claude-plugin/*` manifests.

Success criteria:
- No Claude marketplace installation command is required to complete basic `ooo` flow in Codex.
- Output and behavior align with updated docs.

## Idempotence and Recovery

These steps are designed to be re-runnable:
- Preflight and quality gate commands can be rerun safely; outputs overwrite artifact files.
- Package work is isolated by ownership; failed package can be reset by reverting only owned files.

Failure and retry rules:
1. Stop after two identical failures with unchanged inputs.
2. For each retry, change exactly one variable (code, environment, credential source, or execution context).
3. Record the changed variable in Surprises & Discoveries with evidence.
4. If more than one variable changes in a retry, mark evidence inconclusive and rerun with single-variable discipline.

## Artifacts and Notes

Required artifact directory:
- `.artifacts/execplans/20260306-port-claude-plugin-to-native-chatgpt-codex/`

Minimum required files:
- `preflight.txt`
- `codex-adapter-contract.md`
- `codex-compat-contract.md`
- `mcp-registration-check.txt`
- `mcp-probe.txt`
- `mcp-tool-call-proof.txt`
- `run-context.sh`
- `evidence-identity.txt`
- `evidence-permission.txt`
- `evidence-dry-run.txt`
- `evidence-real-op.txt`
- `checkpoint-1-integration.txt`
- `codex-only-guardrail.txt`
- `final-test-review.md`
- `final-ruff-check.txt`
- `final-ruff-format-check.txt`
- `final-mypy.txt`
- `final-pytest.txt`
- `final-smoke-codex.txt`
- `final-mcp-probe.txt`
- `final-mcp-tool-call-proof.txt`

Artifact absence means milestone incomplete even if behavior appears to work.

## Interfaces and Dependencies

Runtime and interfaces to preserve:
- `src/ouroboros/providers/base.py` defines `LLMAdapter` protocol and must remain the adapter contract.
- New Codex adapter must return `Result[CompletionResponse, ProviderError]` and follow existing error handling semantics.
- Skill routing remains rooted in `skills/*/SKILL.md` definitions and `AGENTS.md` command contract.
- MCP server remains served by `ouroboros mcp serve` unless compatibility contract explicitly requires a different invocation.

Expected new interface (target shape):
- In `src/ouroboros/providers/codex_adapter.py`:

    class CodexAdapter:
        async def complete(self, messages: list[Message], config: CompletionConfig) -> Result[CompletionResponse, ProviderError]:
            ...

Dependency constraints:
- `ClaudeCodeAdapter` may remain in codebase, but no primary-path behavior may depend on it.
- Any new dependency must be added to `pyproject.toml` with tests proving import/runtime behavior.
- Keep frozen dataclass and Result-pattern invariants.

## READY Gate Before PLAN_COMPLETE

Readiness question: Can a medium-reasoning implementation agent execute this plan without additional design decisions?

Answer: Yes. Critical unknowns are resolved by explicit PKG-0 gate and contract artifact before build work; all downstream packages define owned files, dependencies, commands, expected observations, and mandatory evidence.

Change note (2026-03-06): Initial plan authored for Codex-native porting using user prompt as backlog authority because repository-local backlog files referenced by template are absent.

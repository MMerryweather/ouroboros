# Change Target Map

## Priority Order

1. `AGENTS.md` (high bar only)
2. `.ralph/PROMPT_plan.md`, `.ralph/PROMPT_build.md`, `.ralph/PROMPT_master_orchestrator.md`
3. `docs/DOCUMENTATION_INDEX.md`
4. Domain-specific docs under `docs/`

## AGENTS.md High-Bar Rule

Edit `AGENTS.md` only when all are true:

- pattern is cross-domain (planning + build + orchestration) or repeatedly high-cost
- guidance is stable and general, not incident-specific
- rule belongs at global policy layer

If any condition is false, write to detailed docs or prompts instead.

## Prompt Placement Rules

- Planning decomposition failures -> `.ralph/PROMPT_plan.md`
- Build execution/test/update failures -> `.ralph/PROMPT_build.md`
- Child orchestration/retry/handoff failures -> `.ralph/PROMPT_master_orchestrator.md`

## Documentation Placement Rules

- Discoverability/routing updates -> `docs/DOCUMENTATION_INDEX.md`
- Domain operating guidance -> closest `docs/<domain>/*.md`
- Post-incident durable decisions -> `docs/decisions/*.md`

## Collision Rule

If a candidate can be encoded in both AGENTS and detailed docs, prefer detailed docs unless AGENTS high-bar is satisfied.

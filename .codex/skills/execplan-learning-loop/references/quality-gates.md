# Quality Gates

## Gate 1: Abstraction Gate

Pass only if candidate is class-level and uses this shape:

`trigger pattern -> preventive guardrail -> enforcement location`

Reject candidates that mention one-off identifiers, timestamps, or incident-only context without generalization.

## Gate 2: Evidence Gate

Single incidents are allowed. Historical mining is still mandatory.

Evidence is weak/conflicting when:

- root cause class cannot be stated clearly
- enforcement location is unclear
- expected prevention effect is speculative only

If weak/conflicting: no edits, watch-only ledger entry.

## Gate 3: Placement Gate

Pass only if target matches `change-target-map.md` precedence.

## Gate 4: AGENTS High-Bar Gate

If target is `AGENTS.md`, enforce high-bar criteria.

## Gate 5: Change Budget Gate

Per run maximum:

- 1 global rule change
- 3 local prompt/doc edits

Excess candidates become watch patterns.

## Gate 6: Objective Priority Gate

Tie-breakers must favor:

1. repeat-failure prevention
2. autonomy improvement

## Gate 7: Confidence Calibration Gate

Every candidate must declare confidence (`low|medium|high`) with rationale tied to corpus evidence.

Reject candidates with missing confidence/rationale.

Calibration policy:

- If high-confidence candidates underperform repeatedly, tighten thresholds.
- If medium-confidence candidates consistently succeed, promote threshold policy.

## Gate 8: Stale-Rule Pruning Gate

Rules with no measurable impact for `X` runs (default `5`) must be pruned.

Allowed actions:

- demote from global to local documentation/prompts
- refine rule wording and enforcement location
- retire rule to watch-only entry

## Gate 9: Consistency Check Gate

A guardrail is not active unless declared enforcement artifacts exist.

Required checks:

- referenced hook/test/script/workflow file path exists
- referenced prompt/doc section exists or is created in the same run
- missing artifact marks the candidate as `watch-only` until resolved

## Decision Outcomes

- `apply`: gates passed, edits + ledger + taxonomy updates + auto-commit
- `watch-only`: gates failed or low confidence, ledger/taxonomy only, optional commit for persistence

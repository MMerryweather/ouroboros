---
name: execplan-learning-loop
description: Harvest generalized learnings from completed implementation ExecPlans and apply systematic improvements to prompts and documentation so failure classes do not repeat and autonomy improves over time. Use automatically on implementation-complete signals, or manually when requested.
metadata:
  short-description: Systematic learning loop from completed exec plans
---

# ExecPlan Learning Loop

This skill exists for one purpose: systematic learning and continuous improvement of the coding harness.

It converts implementation outcomes into generalized guardrails that reduce repeat failure classes and improve autonomous completion.

## When To Use

Use this skill in either mode:

- `auto`: after implementation-complete detection (completed plan move or all DoD checks complete).
- `manual`: explicit invocation by a human or orchestrator.

Manual default mode is `apply`.

## Inputs

Required:

- Target completed ExecPlan path.

Optional:

- `mode`: `apply` (default) or `dry-run`.
- `history_n`: number of completed plans to mine (default `20`).
- `keywords`: additional search terms for repo-wide plan grep.

## Non-Negotiable Rules

1. Generalize; never write incident-only rules.
2. Mine history before proposing edits: target plan plus last `N` completed plans.
3. Single failure can trigger change, but only after abstraction gate passes.
4. Candidate format is mandatory:
   `trigger pattern -> preventive guardrail -> enforcement location`.
5. If evidence is weak or conflicting: make no edits; log watch pattern only.
6. Respect change budget per run:
   - max `1` global rule change
   - max `3` local prompt/doc edits
7. Keep `AGENTS.md` small. Only edit it for high-cost, cross-domain patterns.
8. Objective priority order:
   - first reduce repeat failure classes
   - second increase autonomous completion rate
9. Every candidate guardrail must carry an explicit confidence score (`low|medium|high`) and rationale.
10. Every run must persist KPI snapshot fields in the ledger:
    - `repeat_class_recurrence_30d`
    - `autonomy_completion_rate`
    - `false_positive_rule_rate`
    - `doc_churn_rate`
11. Every run must persist prediction vs outcome:
    - prediction: expected prevented classes in next `N` plans
    - outcome: whether those classes reappeared in that window (`yes|no|pending`)
12. Perform stale-rule pruning: if a rule has no measurable impact after `X` runs (default `X=5`), downgrade it, relocate it from global to local docs, or retire it.
13. Run consistency checks: do not count a rule as active unless declared enforcement artifacts (hook/test/script/path) exist.

## Target Precedence Map

Use `references/change-target-map.md`.

Short version:

- `AGENTS.md`: high-bar cross-cutting policy only.
- `.ralph/PROMPT_*.md`: planning/build/orchestration behavior gates.
- `docs/DOCUMENTATION_INDEX.md`: discoverability/routing.
- `docs/<domain>/*`: detailed operational guidance.

## Execution Workflow

Follow `references/workflow.md` and `references/quality-gates.md`.

Minimum required loop:

1. Verify trigger and de-dup run.
2. Build evidence corpus from completed plans (`N=20` default).
3. Optionally keyword-grep all exec plans for additional signal.
4. Classify findings using taxonomy (`docs/decisions/systematic-improvement-taxonomy.md`), adding new classes when justified.
5. Propose generalized candidate guardrails in required template.
6. Apply quality gates and change-budget constraints.
7. Apply edits in precedence order.
8. Append ledger entry in `docs/decisions/systematic-improvement-ledger.md`.
9. Persist taxonomy updates if new classes were learned.
10. Auto-commit with:
    `chore(skill:execplan-learning-loop): systematic feedback updates [ledger:<entry-id>]`

## Output Contract

At run end, produce:

- `entry_id`
- `run_mode`
- `plans_analyzed`
- `classes_detected`
- `classes_added`
- `watch_patterns`
- `files_edited`
- `global_changes_count`
- `local_changes_count`
- `kpi_snapshot`
- `prediction_window_n`
- `predicted_prevented_classes`
- `prediction_outcome`
- `candidate_confidence_profile`
- `stale_rule_actions`
- `consistency_drift_findings`
- `commit_hash`

If no edits are applied, still append a ledger entry (`watch-only`) and commit ledger/taxonomy updates when present.

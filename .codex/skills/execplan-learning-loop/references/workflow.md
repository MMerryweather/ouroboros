# Workflow

## 1) Trigger And Run-Key

Accepted triggers:

- Auto: implementation-complete signal detected by orchestrator/build loop.
- Manual: explicit invocation.

Implementation-complete means either:

- ExecPlan moved to `docs/exec-plans/completed/`, or
- The ExecPlan has all items checked in both `Progress` and `Definition of Done`.

Create `run_key`:

`<plan-path>::<latest-commit-touching-plan>::<mode>`

If `run_key` already exists in the ledger, skip edits and write a short dedup note.

## 2) Build Corpus

Primary corpus:

- current completed plan
- last `N` completed plans (`N=20` default)

Useful commands:

    ls -1t docs/exec-plans/completed/*.md | head -n 20
    rg -n "^## Surprises|^## Decision Log|^## Outcomes|BLOCKED|retry|failed|timeout|handoff|checkpoint" docs/exec-plans/completed/*.md

Optional keyword expansion:

    rg -n "<keyword1>|<keyword2>|<keyword3>" docs/exec-plans/**/*.md

Also load recent ledger history to support KPI and calibration updates:

    rg -n "^### `sil-|^- Classes detected:|^- Gate outcome:|^- Applied changes:|^- Objective impact:" docs/decisions/systematic-improvement-ledger.md

## 3) Extract And Classify Findings

For each finding, record:

- symptom
- root cause class
- recurrence hints in corpus
- autonomy impact
- prevention leverage

Map each finding to taxonomy class in:

- `docs/decisions/systematic-improvement-taxonomy.md`

If no class fits, add a new class with definition and inclusion/exclusion rules.

## 4) Generate Candidate Guardrails

Every candidate must use:

`trigger pattern -> preventive guardrail -> enforcement location`

For each candidate, also record:

- confidence: `low|medium|high`
- confidence rationale: why this confidence is justified from the evidence corpus
- predicted prevented classes in next `N` plans (default `N=5`)

Example format:

- Trigger pattern: repeated incomplete preflight evidence before expensive tests.
- Preventive guardrail: require preflight artifact paths and fail-fast stop condition.
- Enforcement location: `.ralph/PROMPT_build.md` and `docs/PLANS.md` link note.

## 5) Apply Gates

See `references/quality-gates.md`.

If candidate set fails gates, do not edit prompts/docs. Append watch-only ledger entry.

Before counting a candidate as actionable, run consistency checks:

- declared enforcement location exists in repository
- if enforcement claims hook/test/script, the artifact path exists
- if enforcement claims CI gate, workflow path exists

## 6) Apply Edits By Precedence

Follow `references/change-target-map.md` and per-run budget:

- max 1 global rule change
- max 3 local edits

Global means `AGENTS.md` or equivalent root policy.

## 7) Persist Learning

Append run entry to:

- `docs/decisions/systematic-improvement-ledger.md`

Update taxonomy file when needed:

- `docs/decisions/systematic-improvement-taxonomy.md`

Mandatory ledger fields per run:

- KPI snapshot:
  - `repeat_class_recurrence_30d`
  - `autonomy_completion_rate`
  - `false_positive_rule_rate`
  - `doc_churn_rate`
- prediction:
  - `prediction_window_n`
  - `predicted_prevented_classes`
- outcome:
  - `classes_reappeared_within_window` (`yes|no|pending`)
- calibration:
  - `candidate_confidence_profile`
- consistency:
  - `consistency_drift_findings`
- pruning:
  - `stale_rule_actions`

Stale-rule pruning policy:

- default stale window: `X=5` runs
- if no measurable impact after `X` runs, choose one:
  - demote global rule to local docs/prompts
  - tighten guardrail wording
  - retire rule and keep watch-only pattern

## 8) Commit

Auto-commit required:

    git add <edited-files>
    git commit -m "chore(skill:execplan-learning-loop): systematic feedback updates [ledger:<entry-id>]"

No extra validation is required in this skill. Keep it DRY and rely on other quality skills and loops.

## 9) Self-Improvement Calibration

Compute and persist KPI snapshot each run (rolling 30-day window):

- `repeat_class_recurrence_30d`:
  recurring class events / total class events.
- `autonomy_completion_rate`:
  successful `apply` runs with completed commit / total runs.
- `false_positive_rule_rate`:
  predicted-prevented classes that reappeared within prediction window / total predicted-prevented classes with resolved outcomes.
- `doc_churn_rate`:
  total files edited by this skill / runs in window.

Update prediction outcomes:

- For each prior entry with pending outcome where `prediction_window_n` has elapsed, mark:
  - `yes` if any predicted class reappeared in the observed window.
  - `no` if none reappeared.

Calibration policy:

- If false-positive rate increases for two consecutive windows, lower confidence for similar candidate types and tighten gate thresholds.
- If high-confidence candidates repeatedly miss outcomes, downgrade to medium by default until recalibrated.
- If medium-confidence candidates repeatedly succeed, permit promotion to high with rationale.

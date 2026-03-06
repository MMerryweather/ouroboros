# Systematic Improvement Taxonomy

## Class: execution-context-constraints
Definition: Validation or test commands fail due to sandbox/home-directory/network constraints rather than product logic.
Include: `Errno 30`, permission-denied runtime setup, sandbox-only path write failures.
Exclude: Actual application permission bugs.

## Class: guardrail-doc-drift
Definition: Primary-path documentation drifts from guardrail requirements and fails automated policy checks.
Include: banned legacy phrasing inside primary markers, missing required marker blocks.
Exclude: copy edits outside enforced guardrail scope.

## Class: post-implementation-hygiene
Definition: Non-functional regressions discovered only in review/final gates after implementation appears complete.
Include: import sort/format drift, missing fresh artifact evidence.
Exclude: functional correctness defects caught by package-local tests.

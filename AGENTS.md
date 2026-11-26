# Flutter Harness contributor instructions

Deterministic-first, CLI-first, reuse-first. Keep one coherent runtime;
no compatibility fallback paths, unnecessary dependencies, skills or
new agent roles. Use native CLI and code for mechanical operations, the
model for semantics. Keep the generated project instructions compact
and update canonical docs/tests with runtime changes. Preserve product
foundation and owner-only merge. Do not weaken gates to obtain green CI.

Run Bash syntax checks, Python unittest discovery, Node guard tests and
the existing real starter CI. No extra device or model evaluation suite. For reusable Harness gaps, reproduce the failure, add the smallest durable regression protection and remove superseded rules where safe. Use the existing Lab for explicit before/after evaluations (docs/engineering-evolution.md), not as an additional per-task gate.
Report exact outcomes and limitations. Stage only task files, never merge
or force-push automatically.

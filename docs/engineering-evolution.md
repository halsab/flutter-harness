# Evidence-driven engineering evolution

The goal is fewer defects and less manual intervention, not more agent calls.
Keep one Build parent, one branch, risk-based read-only review, existing
canonical check, exact candidate receipts, independent CI and owner approval.
No automatic merge, additional skills, default MCP or worker swarm.

## Where a lesson belongs

1. Reproduce a material failure or establish a concrete static proof.
2. Fix the cause at the narrowest responsible boundary.
3. Prefer an existing type/API, analyzer rule, behavior test or CLI capability;
   add a custom deterministic check only for a reusable, observable invariant
   that the existing mechanisms cannot enforce. Test a failing case and a valid
   case; avoid rules that merely encode one app's product choices.
4. Keep application-specific tests and contracts in the app. If a confirmed
   failure exposes a reusable Harness gap, record a short section in the
   existing task PR (failure, cause, proposed protection, evidence). No
   mandatory report, additional model call, managed-file edits or new gate.
5. The maintainer triages the lesson in a separate Harness change, reproduces
   it with a fixture, implements the smallest correction, runs existing CI,
   and removes superseded rules where their guarantees are demonstrably
   preserved. Roll out through the existing managed installer after approval.
   Do not silently self-modify an installed Harness.

Example: missing data and corrupted persisted data must not share a success
result when loss is possible. Fix the app repository contract and seed a
regression test; do not add a universal grep ban on catch blocks. A guard that
classifies an untracked destructive operation differently from the identical
committed tree is a Harness defect: use a Git fixture to verify equal risk and
candidate identity before staging, after staging and after commit.

## Lab evaluation (explicit maintainer exercise)

Use flutter-harness-lab and ordinary disposable branches/worktrees, without
adding a task-time benchmark service. Compare an exact baseline Harness
revision and a proposed revision using the same clean app commit, SDK,
OpenCode configuration/model/effort, initial fixture, task text and runtime
target. Install each revision in its own clean checkout and start a fresh
Build session. Do not use a previous session or let one result seed the other.
Record the actual commit IDs, environment and deviations; repeat if model
variance makes the result inconclusive.

Representative tasks (seed or select a suitable fixed app revision first):

| Scenario | Required observable outcome |
| --- | --- |
| Routine text change | Exact requested text; no gratuitous review or runtime matrix |
| Interacting filter/search/sort | Independent controls, stable saved order, exact grouped outcomes |
| Rejected persistence write | Seeded prior data remains after reload; recoverable input |
| Corrupt stored payload | Distinct failure, no destructive reset or overwrite |
| Material screen redesign | Populated runtime evidence, accessible controls and both themes as required |
| Delivery failure/retry | Structured error or one verified PR for the exact candidate; no duplicate PR |

Use the existing receipts, diagnostics --local, session usage and actual
PR/CI results. Review product acceptance against an independent fixed expected
outcome, not against the generated test suite alone. Compare success, escaped
material defects, false-positive findings, manual interventions, elapsed
time, canonical check attempts, reviewer calls and available token counters.
Record unavailable values as NOT MEASURED, not zero; usage counters are not
billing totals. No token-saving claim without actual matched measurements.
Do not require a new model, device matrix or benchmark on routine tasks.

Accept a revision when required behavior and safeguards are preserved and
observed trade-offs are acceptable to the owner. Deterministic CI is necessary
but not proof of semantic agent performance. A blocked or unrun Lab exercise
must be explicitly disclosed, not represented as a passed comparison.

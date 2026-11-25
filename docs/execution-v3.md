# Execution v3 — controller decision and migration

Status: hardened existing execution path; external controller is a deferred design option, not a release dependency. No production claim for the future controller.

## Evidence: Lab #38, #39 and interrupted add-dialog trial

The trials took 7:01, 18:00 and 51:29 respectively. The third task never delivered. Its recorded session has 105 tool calls, five standard checks, two 600s test timeouts, eight final captures and one High reviewer dispatch. It launched the original candidate but did not record a valid baseline capture before editing. The last check passed; publication remained blocked after review disagreement. The actual reviewer findings and images are not available for independent verification. Do not assume the review was wrong.

## Audit

- CLI owns source and delivery receipts; quality.mjs separately infers check success from tool output and keeps volatile review state. This duplicates the authority for acceptance.
- index.js relies on experimental.idle, background completion and a small generic retry budget. Background completion did resume the trial, but the parent spent repeated long cycles on test repair and no independent dispute path existed.
- resources.mjs denies repeated identical review keys. That prevents repeated asking for PASS, but conflates ungrounded findings and confirmed defects.
- Visual receipt validation historically only required a different digest for baseline, not the actual initial candidate. Missing baseline is self-reported. Batch capture repeats all states.
- diagnostics previously required recorded session IDs, export success and a valid installation. An unfinished run must be diagnosable without a model.
- check.sh allowed tests to continue after first failure and gave the entire test process 600s. Failure summaries were generic.
- task-plan.py is a declarative dependency helper, not an execution engine. Do not make it mandatory for focused tasks.

## Target

One durable controller owns lifecycle transitions. OpenCode is a bounded model executor; native SDK/CLI remains the implementation mechanism. Keep product standards, managed revision checks, exact candidate fingerprint, one pinned runtime, independent CI, owner publication approval, idempotent delivery. No automatic merge, no default MCP, no automatic premium escalation.

Controller state: NEW -> PREPARED -> BASELINE (visual only) -> IMPLEMENT -> CHECK -> VISUAL (required only) -> REVIEW (risk only) -> READY_TO_DELIVER -> DELIVER -> COMPLETE.

Failures: CHECK -> REPAIR -> CHECK; material review finding -> REPAIR; missing evidence -> EVIDENCE; disputed finding -> ADJUDICATE once, then confirmed repair or evidence-bound independent PASS, otherwise BLOCKED. External permission/revision/device blockers stop at explicit terminal state with resume information, never trigger unrelated repair. A running subprocess is not a completed phase. Every transition is based on observed durable receipts, with task/base/candidate identifiers; interrupted or expired attempts never become PASS. Resume from receipts, not chat summaries. A changed source invalidates affected evidence; unchanged inputs never require a full rebuild.

Prefer a foreground Python supervisor driving bounded OpenCode runs via documented opencode run --format json / --session (or supported service API if needed). Verify the actual installed V2 runtime, event schema, permission behavior, image attachment and cancellation on the local machine before replacing the guard. Do not use --auto to approve publication. Controller handles GitHub publication only with explicit owner approval and equivalent independent review/receipt checks. Keep the legacy guard active until replacement passes parity tests; do not run competing orchestrators. No invented plugin dispatch API.

## Migration

1. Foundation (this PR): deterministic bounded check runner, failure report, check lock, diagnostics independent of session export, exact initial baseline digest. Unit tests and existing starter CI. This does not fix review dispute or replace the execution loop.
2. Controller prototype: pure transition table and fake executor, test normal flow, interrupted/late tool result, timeout, failed test, changed candidate, external blocker, missing baseline, stale review, disputed finding, owner denial, delivery retry, restart. Durable task record and one transition authority. Measure invocation count before real model runs.
3. OpenCode adapter: locally verify CLI version/flags, actual JSON event schema and model/permission behavior; prove no hidden background work after run ends. Integrate native runtime evidence and independent reviewer. Remove redundant idle recovery and text-based check status only when equivalent gates are proven.
4. Lab trials on clean branches, one small task at a time. No manual repair to count as autonomous success. Target ordinary small task: one baseline launch, one checked final launch, one review, one PR; repeated steps only after real defects or new inputs. Track wall time, input/cache tokens, model effort, tool counts, actual phase outcomes. Do not confuse mock success with actual simulator/agent success.

## Required regression cases

A failing test stops before a hanging later test; hung process is bounded and not PASS. A duplicate check cannot invalidate an active one. A missing session export still writes local diagnostics. An unrelated baseline hash is rejected. Later stages must add executable controller and adapter tests before any production cutover.

## Release decision

Do not hold practical development for a speculative external supervisor. Ship the hardened existing CLI and guard first. A full external controller remains a future option only if actual production use demonstrates a need; it is not implemented or required for this release. Existing OpenCode background completion is observed in Lab logs. Keep exact current receipt and owner approval, automatic original capture, bounded review adjudication, and reuse of valid scripted evidence. A real local smoke check remains necessary; CI mocks do not prove OpenCode plugin runtime or UI appearance.

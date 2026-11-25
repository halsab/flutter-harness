# Deterministic architecture (schema 2)

OpenCode is the existing model runtime, not reimplemented. The agent owns
intent, design, source changes, acceptance selection and hard diagnosis.
The installed Python CLI coordinates native tools, configuration, receipts,
branch setup, scaffold, validation, runtime and delivery. Small Bash/Python
helpers are implementations of that CLI, not competing workflows.

- Install/sync: source revision and content hashes; preflight all collisions,
  keep unmanaged app source, explicit legacy adoption, Git rollback.
- Fresh setup: Flutter SDK generation, Material starter, dependency setup,
  test, commit. Existing app semantic migration is agent work.
- Configuration: explicit profile, integration branch, managed revision.
- Verification: standard once, exact candidate receipts, separate risk review.
- Runtime: real platform tools, explicit target, one representative platform,
  reusable scenarios and captures; never infer E2E from screenshots.
- Delivery: approved canonical command, exact task files, current base,
  candidate check and PR head verification. Resume from actual Git/PR state.
- Recovery: bounded OpenCode idle repair prompts; no progress stops.
- Telemetry: machine-generated check/PR receipts and session export counters.

The quality hook checks actual tool results and child review outcome; the
CLI checks current content receipt, not a model-authored PASS string.
The two mechanisms are workflow guardrails, not a sandbox. GitHub CI and
branch restrictions remain independent server-side controls.

No default skill, MCP or custom context summarizer. Use OpenCode's search,
context and model routing; load only the relevant canonical product guide.
No automatic multi-agent dispatcher for ordinary work. Explicit complex
work may use the graph helper for dependencies and file conflicts; actual
child completion is observed by the resource guard; delivery waits for it.
Integrated acceptance is separate. Do not turn
abstract graph declarations into a false delivery guarantee.

## Execution redesign (decision, staged migration)

The current plugin remains the delivery guard during migration. See [Execution v3](execution-v3.md) for the audit, target controller, gates and acceptance criteria. The first stage moves check supervision to a bounded Python runner and makes diagnostics independent of model/session availability; it does not yet replace idle recovery.

## Worktree isolation

Owner-side workspace.py is a thin Git/CLI manager, not another agent. Separate worktrees and durable platform leases isolate state and runtime; cumulative detached integration checks produce ordered exact-tree evidence. See [Worktrees](worktrees.md).

# Automated evolution

No product registration, Lab dependency, central polling, extra app CI secret,
or model call for report transport. Installed Harness uses existing gh
authentication to the fixed central repository halsab/flutter-harness.

## Reporter

By default on local runs, selected typed DeliveryBlocked errors (invalid repo
or PR responses and PR identity/URL mismatch) enqueue a report. Build can also
invoke the installed CLI lesson command for a confirmed reusable gap using its
finite list of categories. A report is an unconfirmed signal, not proof that
Harness is defective. Ordinary test/analyzer failures, permissions, network
outages and generic invariants are not reported automatically.

The only public payload is schema, Harness commit SHA, catalog code and an allowlisted delivery stage (unspecified for semantic reports).
No source, project identifier, local path, prompt, stderr, URL, screenshot,
token or arbitrary text. Only the authenticated halsab account can publish.
Set HARNESS_REPORTS=off to disable all reporting; CI is always excluded.
A local queue and receipts live under ignored .flutter-harness/work/lessons.
Transport is synchronous, bounded per GitHub API request, and never a delivery
gate. At most one queued item is retried at begin. Each code+revision+stage is
deduplicated locally and against owner Issues, including closed Issues.
Concurrent first submissions from separate machines can still race; do not
treat issue creation as an exactly-once distributed transaction. Report data
does not identify a project, and recurrence on a new revision is a new signal.

## Central Evolution (one-time setup)

In the central Harness repository Settings -> Secrets and variables -> Actions:

- Secret OPENAI_API_KEY: restricted OpenAI API project key for the official
  Codex Action. This uses separate API billing, not local OpenCode or the
  ChatGPT subscription.
- Secret HARNESS_EVOLUTION_TOKEN: fine-grained GitHub PAT limited to
  halsab/flutter-harness with Contents and Pull requests read/write and
  Metadata read. It is used only in the publish step; no Actions/workflows
  permission needed. Use an expiring token. This separate token enables normal
  PR CI without the GITHUB_TOKEN-created PR approval restriction.
- Repository variable HARNESS_EVOLUTION_ENABLED=true (explicit activation).

The central queue is processed Monday and Thursday (04:23 UTC), one canonical
owner issue per run, globally serialized. This scans only Issues in Harness,
never other projects. An attempted label is reserved before paid work;
identical reports, including concurrent duplicates, are excluded after an
attempt or closure. No model calls for an empty queue or missing credentials.
Owner-only workflow_dispatch may explicitly investigate an unattempted issue
outside the schedule. To deliberately retry, remove the attempted label
from the report (and any exact attempted duplicate) first; no auto retries.
GitHub can disable scheduled workflows after 60 days of repository inactivity.

The investigator is fixed to GPT-6 Luna / low effort with a ten-minute job
timeout; no default premium model, escalation or additional agent. Two
scheduled investigations per week is a run limit, not a hard monetary or
token cap. Use a separate API project/key with appropriate rate and spending
controls; monitor actual API costs. Manual dispatch is outside the scheduled
limit. Until enabled, Issues accumulate without paid calls.

Only owner-created canonical open issues on main are accepted. Public
third-party issue text never enters a model prompt; the strict schema
reconstructs it from fixed descriptions, a commit SHA and an allowlisted
stage. An insufficient signal stays open without a speculative patch.

The investigation job has read-only repository access, no persisted Git
credentials, no publication token, bounded time and an isolated Codex
workspace with sudo dropped. If there is no reproducible defect, the agent
should produce no patch; issue remains open. Patch is handed to a separate
credential-free verification job. A trusted copy of the original validator
rejects out-of-scope, binary, special-mode, oversized and testless changes.
Automated fixes must add regression test lines without removing existing ones. In a disposable local Git worktree the original targeted tests must pass, and the same tests with only the new test changes must fail against the original source. Then the clean committed candidate must pass the existing deterministic suites before a fresh publisher applies the same patch without executing candidate code. Publication uses one fixed branch
per issue, never force-pushes or merges; the full existing PR CI and owner
review remain required. The baseline failure is mechanical evidence, not a proof of semantic correctness; an unrelated assertion or import error can still mislead, so review the actual defect and test during owner approval.

No autonomous change to installed Harness or its release process. A merged
PR closes the issue normally through GitHub's closing reference. Failed or
unreproduced reports remain open. Automatic merging and auto-updates are not
enabled. This is intentionally narrow; installer and guard failures without
an explicit semantic report are not captured automatically yet. The catalog
can grow only with specific proven classes and regression coverage.

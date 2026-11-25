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

The only public payload is schema, Harness commit SHA and catalog code.
No source, project identifier, local path, prompt, stderr, URL, screenshot,
token or arbitrary text. Only the authenticated halsab account can publish.
Set HARNESS_REPORTS=off to disable all reporting; CI is always excluded.
A local queue and receipts live under ignored .flutter-harness/work/lessons.
Transport is synchronous, bounded per GitHub API request, and never a delivery
gate. At most one queued item is retried at begin. Each code+revision is
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
  Optional HARNESS_EVOLUTION_MODEL selects a supported Codex model; otherwise
  the official action default is used. Reasoning effort is medium.

Only owner-created canonical open issues on main can trigger work; public
third-party issues cannot trigger a paid model call. No issue text is passed
as instructions; strict schema validation reconstructs a prompt from fixed
descriptions and a validated commit SHA. Each new issue has one automatic
attempt. Existing issues or failed runs can be retried via owner-only
workflow_dispatch with issue number. Until enabled, Issues accumulate without
paid calls. If secrets are missing, the enabled workflow fails visibly.
No periodic poll or unlimited automated retries.

The investigation job has read-only repository access, no persisted Git
credentials, no publication token, bounded time and an isolated Codex
workspace with sudo dropped. If there is no reproducible defect, the agent
should produce no patch; issue remains open. Patch is handed to a separate
credential-free verification job. A trusted copy of the original validator
rejects out-of-scope, binary, special-mode, oversized and testless changes.
Existing deterministic tests are run before a fresh publisher applies the
same patch without executing candidate code. Publication uses one fixed branch
per issue, never force-pushes or merges; the full existing PR CI and owner
review remain required. A test change is not proof that a regression really
fails on the original implementation; inspect evidence during owner review.

No autonomous change to installed Harness or its release process. A merged
PR closes the issue normally through GitHub's closing reference. Failed or
unreproduced reports remain open. Automatic merging and auto-updates are not
enabled. This is intentionally narrow; installer and guard failures without
an explicit semantic report are not captured automatically yet. The catalog
can grow only with specific proven classes and regression coverage.

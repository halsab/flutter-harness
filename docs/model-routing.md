# OpenCode model routing (ChatGPT Plus)

This harness uses project-level model preferences in `opencode.jsonc`; it does not store credentials.

| Work | Agent | Model | Reasoning |
| --- | --- | --- | --- |
| Implementation, tests, tool runs and PR preparation | `build` (default) | GPT-6 Luna | high |
| Manual planning | `plan` | GPT-6.2 Sol | medium |
| Delegated architecture and hard diagnosis | `architect` | GPT-6.2 Sol | medium |
| Independent review | `reviewer` | GPT-6.2 Sol | medium |
| Routine delegated tasks | `general` | GPT-6 Luna | medium |
| File search and codebase exploration | `explore` | GPT-6 Luna | low |
| Session compaction, titles and summaries | `compaction`, `title`, `summary` | GPT-6 Luna | low |

## Setup and verification

1. In OpenCode run `/connect`, choose OpenAI and **Sign in with ChatGPT** to use an eligible ChatGPT plan. Do not supply an OpenAI API key if your intention is to use subscription usage.
2. Open the Flutter project, run `opencode service restart` in a terminal and start a **new session**. OpenCode loads the project config from the repository root.
3. Check that the models are available using `opencode models` or `/models`. Verify the selected session model and variant; a model named in a config file alone does not prove the provider permits it.
4. Inspect the effective settings with `opencode debug config`; redact any secrets before sharing logs.
5. Use the default `build` agent as the Luna-led orchestrator. A short feature request is sufficient; the project skill directs `build` to delegate substantive design to `architect` and obtain a focused `reviewer` pass without being prompted each time. A subagent uses its configured model; switching primary agents in an existing session **does not necessarily switch the session's selected model**.
6. If you manually use the primary `plan` agent, start a new session and explicitly select GPT-6.2 Sol **medium**; then start a fresh Luna coding session. Keep Sol at or below medium.

The initial setup is **not** a hard spending or usage cap. The subscription has included allowance and limits; additional credits require a separate opt-in where applicable. Check ChatGPT **Settings → Usage** for usage by connected apps and any app limits. Avoid repeated full-codebase analysis, needless subagent calls and very long sessions.

Model identifiers used by this profile: `openai/gpt-6.2-sol` and `openai/gpt-6-luna`. Reasoning variants are selected with `#low`, `#medium` or `#high` on agent model references. No authentication tokens belong in this repository.

Reference: https://opencode.ai/docs/agents, https://opencode.ai/docs/models, https://opencode.ai/docs/providers.

## Short-prompt autonomy vs. interactive design

The default profile intentionally has no Superpowers plugin. Superpowers
`brainstorming` requires a separate human design approval even for simple
requests, as observed in the first lab trial. Instead the first-party
`flutter-harness` skill interprets a direct feature request as authorization
to choose routine, reversible technical details and proceed through plan,
implementation, tests, review and PR preparation. It must not guess material
product requirements or bypass explicit permission checks.

A user can separately opt into Superpowers for interactive design sessions;
the upstream skill's approval rules must then be honored. In particular,
`opencode run` is a one-turn CLI invocation, not an unattended job supervisor.
A required Git push, external-directory access or other approval may still
interrupt that turn and require an interactive session. An agent must report
BLOCKED rather than claim an uncreated PR.

## Safety and approval boundaries

- Each project's OpenCode V2 `permissions` rules ask before access outside
  its workspace or worktree and before `git push` / `gh api` operations.
- The common `gh pr merge` command, force-push patterns, releases and
  `flutter pub publish` are denied by project policy. Project owner merges PRs
  in GitHub after review.
- `architect` and `reviewer` deny edits and all shell commands by default;
  they allow only read-only `git status`, `git diff`, `git show` and
  `git log`. Routine test execution belongs to `build`.
- These rules **are not a security sandbox**. Shell argument parsing is
  best-effort; alternate commands, APIs and external MCP tools may mutate
  state. Never treat a `deny` rule as a substitute for human approval or
  repository-side branch protection. Do not evade a denied operation.
- Enable branch protection/rulesets for the lab's `main` and `app` branches
  in GitHub Settings → Rules → Rulesets (or Branches). Block force pushes,
  require PRs and the relevant passing CI check. These settings may require
  manual repository administration and are not applied by this template.

## Automated checks

From the `flutter-harness` repository root:

```bash
python3 scripts/validate-opencode.py templates/opencode-mobile.jsonc mobile
python3 scripts/validate-opencode.py templates/opencode-mobile-web.jsonc mobile-web
```

The checks use Python's standard library and **do not call any LLM**. The
harness CI checks both profiles and installs each twice to test idempotency.
The lab CI checks its own agent/model/permission configuration. CI cannot
validate real ChatGPT authentication, the currently selected session model,
reasoning effort accepted by a provider, or subagent handoff: test those in a
new local OpenCode session with actual tool output. Keep the Sol default at
medium and avoid repeatedly launching unnecessary review subagents.

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
5. Use the `build` agent as the Luna-led orchestrator. Before substantial work ask it explicitly to delegate design to `architect`, and request `reviewer` once before the PR. A subagent uses its configured model; switching primary agents in an existing session **does not necessarily switch the session's selected model**.
6. If you manually use the primary `plan` agent, start a new session and explicitly select GPT-6.2 Sol **medium**; then start a fresh Luna coding session. Keep Sol at or below medium.

The initial setup is **not** a hard spending or usage cap. The subscription has included allowance and limits; additional credits require a separate opt-in where applicable. Check ChatGPT **Settings → Usage** for usage by connected apps and any app limits. Avoid repeated full-codebase analysis, needless subagent calls and very long sessions.

Model identifiers used by this profile: `openai/gpt-6.2-sol` and `openai/gpt-6-luna`. Reasoning variants are selected with `#low`, `#medium` or `#high` on agent model references. No authentication tokens belong in this repository.

Reference: https://opencode.ai/docs/agents, https://opencode.ai/docs/models, https://opencode.ai/docs/providers.

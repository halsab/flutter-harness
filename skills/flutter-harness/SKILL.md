---
name: flutter-harness
description: Use when developing, testing, diagnosing or preparing a PR for a Flutter project with Flutter Harness installed.
---

# Flutter Harness

Use a lightweight, test-driven workflow: inspect the project, define acceptance criteria from the user's request, make a concise implementation plan, implement incrementally, test, review, and open a PR. Use official Flutter/Dart tools for source and runtime diagnosis. Maestro is for mobile UI exploration and repeatable flows. If the profile includes Web, use Playwright for browser E2E and Chrome DevTools for diagnostics.

## OpenCode model routing

The project `opencode.jsonc` selects models and reasoning effort by agent:
- `build` uses GPT-6 Luna high for implementation, debugging, running tests and preparing a PR.
- `plan` and the `architect` subagent use GPT-6.2 Sol medium for design, trade-offs, acceptance criteria and difficult diagnosis.
- The `reviewer` subagent uses GPT-6.2 Sol medium for an independent code/test review before a PR. Use focused reviews rather than repeatedly reviewing unchanged files.
- `explore` uses GPT-6 Luna low for repository search; `general` uses Luna medium for routine delegated work.
- `compaction`, `title` and `summary` use Luna low for maintenance work.

When working as `build`, delegate substantive upfront design or complex diagnosis to `architect`; use `reviewer` for a focused final review. Do not use Sol for mechanical file search, formatting or simple tool invocations. Never silently raise Sol reasoning above medium.

Do not assume that switching between primary `plan` and `build` in an existing OpenCode session switches the selected model: session model selection is sticky. For reliable routing use named subagents, or start separate sessions with the intended model and reasoning variant. A configured model is not a verified model call; check actual tool outputs and session/model selection.

## Default autonomy policy

- A direct feature request is permission to implement **within the stated scope**. For example, "make a to-do list with persistence" authorizes a reasonable local persistence choice; do not stop to ask whether JSON or SQLite is preferred. State a short assumption and proceed.
- Do not ask the user to choose libraries, file layout, testing commands, UI details, or other routine reversible implementation decisions. Prefer simple, maintained solutions and few dependencies. Record decisions in the PR.
- Ask one targeted question only if missing information materially changes the *requested behavior* (such as whether data must sync across devices), or for irreversible, destructive, costly, security-sensitive, or credentialed actions. Do not manufacture alternatives requiring approval.
- The default autonomous profile intentionally does **not** load Superpowers: its `brainstorming` skill requires a separate design-approval turn before any implementation. This conflicts with single-prompt development. Do not invoke it in autonomous mode. Superpowers can be opted into separately for interactive design work, but an agent in that mode must honor its approval gates.
- Do not silently treat a user's request as approval for protected operations: Git push, external directories, golden baseline changes and merging retain their independent rules. If a tool requires permission, request it rather than bypassing it.
- If an explicit user request is exploratory ("help design", "compare architectures"), collaborate rather than implementing. A concise request to build a well-scoped feature should reach a working PR without additional routine questions.
- An OpenCode `run` command is one turn, not an unattended daemon. If a permission or material clarification gate is reached, report it as BLOCKED; do not claim a finished PR.

## Safety and approval

Follow the project's `permissions` in `opencode.jsonc`. External paths,
Git pushes and potentially destructive shell operations require approval.
Never try alternate shell commands, MCP tools or APIs to bypass a denied
action. Never merge PRs, force-push or publish a release on the user's behalf.
An approval prompt from OpenCode is not the same as a GitHub branch-protection
rule; the owner reviews merges. The `architect` and `reviewer` subagents
may inspect files and read-only Git history but must not edit or run builds.
The `build` agent performs tests and reports actual tool output.

## Workflow

1. For v0, start from a newly created default Flutter SDK project. Inspect its baseline and read `.flutter-harness/config.json`; do not assume Web is enabled. Do not attempt legacy-project migration or retrofit.
2. Derive scope and testable acceptance criteria from the user's request; select conventional defaults independently. Ask only for a genuinely blocking ambiguity or protected action. Create a feature branch before implementation; never commit to main.
3. Draft a concise plan and implement in small, verified increments. Add unit/widget tests for new behavior and commit each meaningful milestone.
4. Prefer official Flutter/Dart commands and the harness scripts over ad hoc shell commands.
5. Use stable Flutter `Semantics(identifier: ...)` for critical UI selectors.
6. Save Maestro exploration as reusable YAML flows and rerun via CLI.
7. Record PASS, FAIL, SKIPPED and BLOCKED separately. Never claim unexecuted tests passed.
8. For changes to accepted golden screenshots, obtain explicit human approval first; don't silently update baselines.
9. Review the diff and push the feature branch. Open a PR with summary, plan, checkpoint commits, tests, platform evidence and blocked checks.
10. Never auto-merge, publish/store-release or use production secrets.

## Bootstrap checks

Until the Dart CLI ships, run:
`bash /path/to/flutter-harness/scripts/check.sh /path/to/project [quick|standard|full] [mobile|mobile-web]`

Make no claim of successful verification without actual command output.

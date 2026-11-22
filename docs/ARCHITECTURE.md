# Architecture and constraints

## Repositories
- `flutter-harness`: shared tooling, installer, skills and scripts.
- `flutter-harness-lab`: `main` is a Flutter SDK-generated default project; `app` initially points to the **same clean starter**. The agent implements test tasks on branches from the clean baseline and may grow `app` over time.

## Initial scope
- **Only new, clean Flutter SDK projects.** No adoption or migration of existing applications in v0.
- The lab `main` branch remains the clean SDK starter. The `app` branch now adds harness configuration and official Flutter/Dart skills, but still has no agent-authored application feature. Do not prebuild a Task Manager or ship application-specific fixtures from the harness.
- For reproducible evaluations, reset the working copy or branch from the exact clean `main` SHA, not a previously modified `app` branch.
- The `app` branch is for observing agent-written functionality, not testing existing-project installation.

## Intended workflow
1. User states an outcome in plain language; agent derives acceptance criteria and chooses routine implementation defaults without confirmation. Ask only about material product ambiguity or protected operations.
2. Agent creates a feature branch, records a plan, and changes code in small verified steps.
3. Agent commits each meaningful checkpoint.
4. Agent runs relevant static, unit/widget and runtime/E2E checks.
5. Agent pushes the branch and creates a PR with evidence, failures and any BLOCKED checks.
6. Only the human merges; only the human accepts new golden baselines.

## Platform profiles
- `mobile`: Android + iOS, Flutter SDK, Dart MCP and Maestro.
- `mobile-web`: mobile plus Flutter Web, Playwright and optional Chrome DevTools.

## Principles
- Script-first, official-first, deterministic and idempotent operations.
- Keep detailed logs as artifacts; summaries should be short and machine-readable.
- Never claim GitHub CI checked local-only iOS tests.
- Public-repo GitHub Actions standard hosted runners are free, but execution and artifact quotas still matter.
- External network/publication/production secrets are outside the agent's autonomous boundary.
- No self-hosted runner on the owner's MacBook in v0.
- Keep GitHub branch protection for `main` and `app` where available; CLI prompts and model instructions alone are not a security boundary.
- Plan/review subagents are read-only and coding may push only after human approval. Never attempt to bypass denied commands via other tools.
- A default autonomous profile must not load the interactive Superpowers brainstorming approval gate. Interactive design remains opt-in, not an implied prerequisite of small feature work.
- Tools may be visible per selected profile, while skill instructions are loaded as needed.

## Development status

The bootstrap installer, Bash check runner, OpenCode V2 templates, role-specific
model routing, and CI validation are implemented. The owner has verified a
default Flutter project on Android emulator, iOS Simulator and Chrome, basic
Dart/Maestro/Playwright/Chrome DevTools/Xcode MCP calls, and Sol/Luna model
responses. These are *manual* checks, not repeatable device E2E tests.

The initial short-prompt feature trial stopped at an unnecessary interactive
Superpowers brainstorming approval step; the default workflow was adjusted to
choose routine technical defaults autonomously. This behavior still needs a
complete rerun after merging the change.

Remaining milestones: complete agent-authored feature implementation and PR,
reusable Maestro/Playwright flows with evidence, golden approval process, and
the optional Dart orchestration CLI. The CI hosted on Linux does not run iOS
simulators or prove locally authorized MCP model routing.

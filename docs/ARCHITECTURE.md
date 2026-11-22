# Architecture and constraints

## Repositories
- `flutter-harness`: shared tooling, installer, skills and scripts.
- `flutter-harness-lab`: `main` is a Flutter SDK-generated default project; `app` initially points to the **same clean starter**. The agent implements test tasks on branches from the clean baseline and may grow `app` over time.

## Initial scope
- **Only new, clean Flutter SDK projects.** No adoption or migration of existing applications in v0.
- Both lab branches are initially empty default projects. Do not prebuild a Task Manager or ship application-specific fixtures from the harness.
- For reproducible evaluations, reset the working copy or branch from the exact clean `main` SHA, not a previously modified `app` branch.
- The `app` branch is for observing agent-written functionality, not testing existing-project installation.

## Intended workflow
1. User and agent agree on scope and acceptance criteria (Superpowers).
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
- Tools may be visible per selected profile, while skill instructions are loaded as needed.

## Development status
This repository is an **early bootstrap**. Dart CLI, project lifecycle automation,
MCP wiring, full CI and benchmark evaluation are future milestones. Do not treat
the documentation as proof that these are already implemented.

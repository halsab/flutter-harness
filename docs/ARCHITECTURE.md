# Architecture and constraints

## Repositories
- `flutter-harness`: shared tooling, installer, skills and scripts.
- `flutter-harness-lab`: `main` is a Flutter SDK-generated default project; `app` initially points to the **same clean starter**. The agent implements test tasks on branches from the clean baseline and may grow `app` over time.

## Product application architecture

The canonical application baseline is [Product foundation](../templates/product/PRODUCT.md): feature-first MVVM, constructor injection, shared design system and Flutter-only platform profiles. The checker is a convention gate, not a complete semantic verifier. Existing Lab app adopts this in a focused migration; never rewrite the SDK starter on main.

## Initial scope
- **Only new, clean Flutter SDK projects.** No adoption or migration of existing applications in v0.
- The lab `main` branch remains the untouched Flutter SDK starter. Lab PR #5 adds the first agent-authored task manager to `app` when merged; do not ship application-specific fixtures in the reusable harness.
- For reproducible evaluations, reset the working copy or branch from the exact clean `main` SHA, not a previously modified `app` branch.
- The `app` branch is for observing agent-written functionality, not testing existing-project installation.

## Intended workflow
1. User describes the desired outcome. Only material product/architecture ambiguities are discussed; at most one design checkpoint. The technical plan is internal, not separately approved.
2. Agent creates a feature branch in the current checkout and changes code in small verified steps. Ordinary branch/worktree and execution mode choices are not user-facing.
3. Agent commits each meaningful checkpoint.
4. Agent runs relevant static, unit/widget and runtime/E2E checks. Maestro is mobile-only by default; Playwright handles Web; report Android, iOS and Web evidence separately.
5. Agent runs one independent, read-only final diff review (with at most one targeted recheck for a major fix), then requests push permission, pushes and creates a PR with evidence, failures and any BLOCKED checks.
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
- Tools may be visible per selected profile, while skill instructions are loaded as needed. Chrome DevTools stays disabled by default; tool schemas and long outputs consume model context.
- Prefer Luna medium for implementation and review. Sol medium is available for complex architecture or hard diagnosis, not automatic on every feature.
- Default profile does not load upstream Superpowers' repeated interactive plan approvals; optional Superpowers design sessions are deliberately separate.

## Development status

The bootstrap installer, Bash check runner, OpenCode V2 templates, role-specific
model routing, and CI validation are implemented. The owner has verified a
default Flutter project on Android emulator, iOS Simulator and Chrome, basic
Dart/Maestro/Playwright/Chrome DevTools/Xcode MCP calls, and Sol/Luna model
responses. These are *manual* checks, not repeatable device E2E tests.

The first full task-list trial reached PR #5, with passing CI and an iOS Maestro flow. It exposed redundant approvals, repeated reviews and loops, high model/context usage and missing automatic PR handoff. The lean workflow addresses these on paper but requires a new runtime trial before claiming improvement. Additional milestones: Android E2E, reusable Playwright flows, golden baselines and an optional Dart orchestration CLI. The CI hosted on Linux does not run iOS
simulators or prove locally authorized MCP model routing.

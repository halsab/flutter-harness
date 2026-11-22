# Flutter Harness

An experimental, open-source, script-first development harness for Flutter:
Android + iOS, with optional Flutter Web. Built on upstream
[Superpowers](https://github.com/obra/superpowers), official Flutter/Dart AI tooling,
Maestro for mobile UI, and Playwright for optional Web E2E.

**Status: bootstrap / unvalidated on device.** This is not yet a production-ready
autonomous development system. Local Flutter SDK verification is pending.

Copyright (c) 2026 **halsab** — [MIT License](LICENSE).

## Repositories

- Harness: https://github.com/halsab/flutter-harness
- Test lab: https://github.com/halsab/flutter-harness-lab
- Lab `main`: generated unmodified Flutter starter (Android, iOS, Web)
- Lab `app`: minimal Task Manager fixture with widget tests and Maestro smoke

## Initialize the lab once (MacBook)

Prerequisites: Git, Flutter SDK on PATH, Git identity configured, and GitHub
push authentication (for example GitHub CLI `gh auth login` and
`gh auth setup-git`).

```bash
git clone https://github.com/halsab/flutter-harness.git
cd flutter-harness
bash scripts/bootstrap-lab.sh
```

This script clones the lab next to the harness, calls `flutter create` using
the **installed official Flutter SDK**, runs baseline tests, commits and pushes
`main`, then applies the test app to `app`, runs analyze/tests and pushes it.
It never force-pushes or overwrites an existing `app` branch.

If Flutter or Git credentials are missing, follow the actionable error and run
the same command again after fixing the prerequisite.

## Install in any Flutter project

```bash
# From your local flutter-harness clone:
bash scripts/install.sh /absolute/path/to/flutter-project mobile
# or:
bash scripts/install.sh /absolute/path/to/flutter-project mobile-web
```

The installer checks for Flutter in `pubspec.yaml` and adds only missing
project files. It does not overwrite existing agent instructions, skills, or
OpenCode configurations. If `opencode.json(c)` already exists, merge the
selected `templates/opencode-*.jsonc` settings manually after inspecting it.

Current OpenCode adapter targets **OpenCode V2** and pins Superpowers to
`v7.0.2`. MCP binaries (`dart`, `maestro`) must exist locally.
For Web, Node/npm and browser tools are also required; Web MCP dependencies
are version-pinned but not yet integration-tested on the owner's MacBook.

Official Flutter skills can be installed using Flutter's published commands
from the Flutter project root:

```bash
npx skills add flutter/agent-plugins --skill '*' --agent universal --yes
npx skills add dart-lang/skills --skill '*' --agent universal --yes
```

See https://docs.flutter.dev/ai/get-started.

## Verify

```bash
bash scripts/check.sh /absolute/path/to/flutter-project standard mobile
bash scripts/check.sh /absolute/path/to/flutter-project full mobile-web
```

The bootstrap verifier reports format, analyzer, Flutter tests and optional
full builds. It writes logs and TSV summaries inside
`.flutter-harness/artifacts`. **It does not yet run Maestro, Web E2E or live
Dart MCP diagnostics**. Those are planned.

## Intended agent workflow

1. The developer and agent agree on the requirement and acceptance criteria.
2. The agent creates a feature branch and implementation plan.
3. The agent implements in small verified steps, committing each milestone.
4. Deterministic scripts and tools verify the app. Failures are fixed and
   verified again. No golden baselines are accepted without the owner.
5. The agent pushes the branch and opens a PR with evidence. **The owner merges.**

See [architecture](docs/ARCHITECTURE.md). Skills and templates are versioned
here; do not fork Superpowers merely to specialize Flutter behavior.

## Known gaps

- No Dart orchestration CLI yet; bootstrap scripts use Bash.
- No tested simulator runtime/DTD lifecycle, Maestro MCP, full E2E, or golden
  approval UI yet.
- Project installation only creates the first OpenCode config or leaves an
  existing one untouched; no safe automatic JSONC merge yet.
- This repo cannot build on your MacBook from GitHub; run the lab bootstrap locally.

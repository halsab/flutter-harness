# Flutter Harness

An experimental, open-source, script-first development harness for Flutter:
Android + iOS, with optional Flutter Web. Uses a first-party, short-prompt
agent workflow, official Flutter/Dart AI tooling, Maestro for mobile UI,
and Playwright for optional Web E2E.

**Status: local bootstrap validated (November 2026), end-to-end agent feature trial pending.**
The SDK starter has run on an Android emulator, iOS Simulator and Chrome on
the owner's MacBook. Flutter quick/standard/full checks and basic MCP
connectivity were exercised locally. This is **not** yet a production-ready
autonomous development system; reproducible device UI flows and a complete
agent-authored feature PR remain to be validated.

Copyright (c) 2026 **halsab** — [MIT License](LICENSE).

## Repositories

- Harness: https://github.com/halsab/flutter-harness
- Test lab: https://github.com/halsab/flutter-harness-lab
- Lab `main`: generated unmodified Flutter starter (Android, iOS, Web)
- Lab `app`: initially identical clean Flutter starter; the agent grows it through tasks and PRs

## Java setup on macOS (optional, before Android builds)

If `flutter doctor` reports `Could not determine java version` but
Android Studio's bundled JDK works, use the explicit setup script:

```bash
bash scripts/setup-java.sh
```

It selects `/Applications/Android Studio.app/Contents/jbr/Contents/Home`
via `flutter config --jdk-dir`. It does **not** install another JDK or
change the system `java` command, and does change the global Flutter JDK
preference. Java 25 requires Gradle **9.1+** to run Gradle; the actual Android
build must still be verified after generating the Flutter starter. Do not
upgrade Gradle or the Android plugin without checking their compatibility.

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
`main`, then creates and pushes `app` at the exact same clean commit.
It never force-pushes or overwrites an existing `app` branch.

If Flutter or Git credentials are missing, follow the actionable error and run
the same command again after fixing the prerequisite.

If GitHub rejects a workflow file with `without workflow scope`, run
`gh auth refresh -h github.com -s workflow`, then update your local harness
checkout with `git pull --ff-only` and rerun `bash scripts/bootstrap-lab.sh`.
The script resumes by pushing the already-created `main` commit **before**
creating `app`. No manual reset or force push is needed.


## Install in a newly created Flutter project

```bash
# From your local flutter-harness clone:
bash scripts/install.sh /absolute/path/to/flutter-project mobile
# or:
bash scripts/install.sh /absolute/path/to/flutter-project mobile-web
```

For v0, installation and testing target **only fresh SDK-generated Flutter projects**. Existing-project compatibility is explicitly deferred. The installer checks for Flutter in `pubspec.yaml` and adds only missing
project files. It does not overwrite existing agent instructions, skills, or
OpenCode configurations. If `opencode.json(c)` already exists, merge the
selected `templates/opencode-*.jsonc` settings manually after inspecting it.

Current OpenCode adapter targets **OpenCode V2**. The default profile does **not**
load Superpowers: its `brainstorming` skill requires an explicit design-approval
turn even for a small feature, which blocked the first short-prompt lab trial.
Superpowers remains an optional **interactive** design workflow, but its
approval gate must not be silently bypassed. MCP binaries (`dart`, `maestro`)
must exist locally.
For Web, Node/npm and browser tools are also required. The pinned Playwright
and Chrome DevTools MCP servers have responded to basic local tool calls;
full automated browser E2E has not yet been proven.

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
`~/.cache/flutter-harness/<project-name>/` by default (or `HARNESS_ARTIFACTS_DIR`). This keeps the clean lab worktree untouched. **It does not run Maestro UI flows, Web E2E or Dart MCP diagnostics**;
those are separate local checks. The script's full level builds Android APK,
iOS Simulator (on macOS) and Web for the mobile-web profile.

## Models, permissions and verification

OpenCode V2 routes implementation and routine work to GPT-6 Luna and planning,
architecture and focused review to GPT-6.2 Sol (medium reasoning). See the
[model routing and safety guide](docs/model-routing.md). Templates contain no
credentials; authorize your provider locally.

The templates ask before accessing paths outside the project, ask before Git
pushes and GitHub API operations, and deny direct `gh pr merge` and common
force-push or publishing commands. **These are guardrails, not a sandbox:**
shell patterns and MCP tools can have effects beyond command matching. Enable
GitHub branch protection on the lab's `main` and `app` branches and review
every PR before merging.

Run `python3 scripts/validate-opencode.py templates/opencode-mobile.jsonc mobile`
and `python3 scripts/validate-opencode.py templates/opencode-mobile-web.jsonc mobile-web`
to check configured models, roles, permissions and MCP lists without using
model tokens. GitHub Actions runs the same validation and installer smoke
tests; the lab additionally validates its own OpenCode config.

## Intended agent workflow

1. The developer gives a short outcome-oriented request; the agent derives
   acceptance criteria and chooses routine implementation defaults itself.
   It asks only when a missing answer changes the requested behavior or a
   protected operation needs approval.
2. The agent creates a feature branch and concise implementation plan.
3. The agent implements in small verified steps, committing each milestone.
4. Deterministic scripts and tools verify the app. Failures are fixed and
   verified again. No golden baselines are accepted without the owner.
5. The agent pushes the branch and opens a PR with evidence. **The owner merges.**

See [architecture](docs/ARCHITECTURE.md). Skills and templates are versioned
here; do not silently modify or bypass a third-party skill's approval policy.
A single `opencode run` is one turn, not an unattended worker: permission prompts
(e.g. a Git push) may still require interactive approval.

## Known gaps

- No Dart orchestration CLI yet; bootstrap scripts use Bash.
- The first short-prompt lab trial reached an unnecessary design-approval gate
  and stopped before implementation. The default autonomous profile now omits
  that gate; a full feature PR must still validate the change end-to-end.
- Android/iOS simulator runtime, basic Dart/Maestro/Xcode/browser MCP calls
  have been verified manually, but repeatable device E2E, full agent feature
  development and golden baseline approval are **not yet** automated.
- Project installation only creates the first OpenCode config or leaves an
  existing one untouched; no safe automatic JSONC merge yet.
- This repo cannot build on your MacBook from GitHub; run the lab bootstrap locally.
- Existing-project adoption, compatibility and migration are out of scope for v0.
- Every independent harness evaluation should start from the clean lab `main` commit; the `app` branch is a development sandbox, not an installation-compatibility fixture.

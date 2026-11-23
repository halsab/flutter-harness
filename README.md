# Flutter Harness

An experimental, open-source, script-first development harness for Flutter:
Android + iOS, with optional Flutter Web. Uses a lightweight first-party
autonomous workflow, official Flutter/Dart AI tooling, Maestro for mobile UI,
and Playwright for Web. Upstream [Superpowers](https://github.com/obra/superpowers)
remains optional for interactive design sessions.

**Status: experimental (November 2026); second autonomous lab trial complete.**
The SDK starter has run on an Android emulator, iOS Simulator and Chrome on
the owner's MacBook. Flutter quick/standard/full checks and MCP
connectivity were exercised locally. The autonomous trial for editing task
titles reached PR #6 with green CI and Android Maestro / Web Playwright runs.
Its audit found incomplete reviewer shell permissions, no observed iOS Maestro
run and a session-level Luna High override; this revision tightens those
contracts. This is **not yet a production-ready autonomous development system**;
a fresh runtime trial is still required to validate these corrections.

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

Current OpenCode adapter targets **OpenCode V2**. Default profiles intentionally
**do not load Superpowers**, because its mandatory planning approval and
execution-selection steps prevented short-request autonomous delivery and caused
repeated handoffs. Upstream Superpowers is still available as an *optional*
interactive workflow (with its own approval requirements). MCP binaries (`dart`,
`maestro`) must exist locally.
For Web, Node/npm and browser tools are also required. The pinned Playwright
and Chrome DevTools MCP servers have responded to basic local tool calls;
the initial lab trial used Playwright for Web, but the Web flow is not yet
recorded as a reusable Playwright script.

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

OpenCode V2 defaults to **GPT-6 Luna medium** for implementation and focused
final review. **GPT-6.2 Sol medium** is reserved for complex architecture or hard
diagnosis, not called automatically for simple tasks. See the
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
model tokens. These inspect **configuration**, not the active UI-selected
model variant; confirm Luna Medium on the new session's model selector and
audit the session export afterward. GitHub Actions runs the same validation and installer smoke
tests; the lab additionally validates its own OpenCode config.

## Default short-prompt workflow

1. The developer requests a feature in plain language. The agent asks only if
   a material business, privacy or architecture choice is unclear (e.g. local
   versus cloud data). When needed, **one** concise design signoff suffices.
2. The agent creates a feature branch in the current checkout and plans
   internally. **No second approval of a technical plan, no worktree choice,
   and no execution-mode choice.**
3. The agent implements with targeted tests, verifies Flutter analysis/tests,
   discovers both Android and iOS devices, runs affected Maestro UI scenarios
   on available Android **and** iOS targets, and verifies Web with Playwright.
   It checks exact intended post-action state rather than accepting accidental
   duplicate text. Builds are not UI tests. It records a separate
   PASS / FAIL / BLOCKED / SKIPPED result per platform, with evidence.
4. The agent performs **one** focused Luna reviewer pass on the complete
   diff; the reviewer uses separate whitelisted read-only Git commands,
   and reports OPEN if diff coverage is incomplete. Fix confirmed
   important issues and self-check affected behavior. Escalate to Sol only
   for significant technical complexity.
5. The agent commits, requests push approval as required, and **creates the
   PR automatically**. If push is denied, report BLOCKED rather than claiming
   the feature is delivered. **Only the owner merges.**

OpenCode is used interactively (`opencode`) for material decisions and tool
approvals. `opencode run` is a single turn and may stop when approval is
required. Any local `opencode.jsonc` changes must be preserved and excluded
from unrelated feature commits.

`mobile-web` config includes a disabled Chrome DevTools MCP entry; enable
it temporarily for unusual browser diagnostics. The regular Web tool is
Playwright, while Maestro is for mobile devices. Extra MCP tool schemas
consume model context even when not called.

See [architecture](docs/ARCHITECTURE.md). Skills and templates are versioned
here; upstream Superpowers is not forked or silently overridden.

## Measure usage without model calls

Use sanitized session exports from OpenCode. Export both parent and relevant
child sessions to include actual specialist usage:

```bash
opencode session export SESSION_ID --sanitize > /tmp/harness-parent.json
python3 scripts/session-usage.py /tmp/harness-parent.json /tmp/harness-child.json
```

The report shows message counts, input/output/reasoning/cache counters by
agent/model/variant and tool-call counts. Counters are **not a monetary
billing estimate**, and model-context consumption by MCP tools is not a
separate paid model invocation by default. Do not commit exports.

## Known gaps

- No Dart orchestration CLI yet; bootstrap scripts use Bash.
- The first lab feature PR (#5) exposed repeated agent approval and review
  loops. The subsequent autonomous title-edit PR (#6) reached GitHub with
  passing CI and actual Android Maestro/Web Playwright calls, but skipped iOS
  Maestro and had three read-only reviewer command denials. These targeted
  fixes require another local end-to-end trial; no claim of proof until then.
- Project installation only creates the first OpenCode config or leaves an
  existing one untouched; no safe automatic JSONC merge yet.
- This repo cannot build on your MacBook from GitHub; run the lab bootstrap locally.
- Existing-project adoption, compatibility and migration are out of scope for v0.
- Every independent harness evaluation should start from the clean lab `main` commit; the `app` branch is a development sandbox, not an installation-compatibility fixture.

## Lightweight CI and local device checks

Hosted CI only validates shell syntax, config, installation and fast Python tests.
Android/iOS Maestro and Web Playwright E2E are the installed agent's local
responsibility for affected features; they are not unconditional CI jobs.

New installations include `.flutter-harness/bin/maestro.sh`. The Maestro
MCP runs through this project-local launcher (workspace cwd), which locates
Maestro from MAESTRO_BIN, PATH or ~/.maestro/bin, and Java from JAVA_HOME,
ANDROID_STUDIO_JBR, the macOS Android Studio JBR or PATH.

To diagnose the environment, run:

~~~sh
bash .flutter-harness/bin/maestro.sh --check
bash .flutter-harness/bin/maestro.sh test maestro/flows/your-flow.yaml
~~~

Existing OpenCode configurations remain untouched by the installer; merge
the new local MCP command deliberately, then restart OpenCode.

The installer also copies `.flutter-harness/bin/check.sh`. It writes structured
PASS/FAIL/BLOCKED results to a local log directory:

~~~sh
bash .flutter-harness/bin/check.sh . quick mobile-web
bash .flutter-harness/bin/check.sh . standard mobile-web
bash .flutter-harness/bin/check.sh . full mobile-web
~~~

The lab CI fixture omits Web compilation from routine PR checks; the full
Web/Android/iOS builds remain available **locally** through
`bash .flutter-harness/bin/check.sh . full mobile-web`.

After an approved `git push` and `gh pr create`, the agent checks delivery
with `bash .flutter-harness/bin/verify-pr.sh . app` (or the documented
integration branch). It is read-only and returns BLOCKED if the PR is
missing, closed or targets the wrong base; it never bypasses push approval.

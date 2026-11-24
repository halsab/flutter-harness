# Flutter Harness

An experimental, open-source, script-first development harness for Flutter:
Android + iOS, with optional Flutter Web. Uses a lightweight first-party
autonomous workflow, official Flutter/Dart AI tooling, Maestro for mobile UI,
and Playwright for Web. Upstream [Superpowers](https://github.com/obra/superpowers)
remains optional for interactive design sessions.

**Status: experimental (November 2026); lean verification policy under evaluation.**
The SDK starter has run on an Android emulator, iOS Simulator and Chrome on
the owner's MacBook. Flutter quick/standard/full checks and MCP
connectivity were exercised locally. The autonomous trial for editing task
titles reached PR #6 with green CI and Android Maestro / Web Playwright runs.
Its audit found incomplete reviewer shell permissions, no observed iOS Maestro
run and a session-level Luna High override; this revision tightens those
contracts. This is **not yet a production-ready autonomous development system**;
a fresh runtime trial is still required to validate these corrections.

Copyright (c) 2026 **halsab** — [MIT License](LICENSE).

## Product foundation

One default feature-first MVVM architecture and Material 3 on Android, iOS
and Flutter Web (`ui_profile: universal`). Custom styling builds on Material.
Adaptive and Minimal are legacy profile values, not new starter options.
Existing installations need a [reviewed configuration/source migration](docs/material-migration.md). Read [the product standard](templates/product/PRODUCT.md).
Installation adds the policy, product.json (pending adoption), non-destructive
design-system starter and executable architecture/style-import convention check.
The agent adopts the baseline and activates it in the first product PR;
existing app code is not overwritten. The first Lab migration will validate
the actual product workflow. The starter is smoke-tested in CI against
Flutter; actual visual review is required for significant UI changes,
not routine functional tasks.

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

## Lean risk-based testing (default)

Ordinary feature: one standard Flutter check (format, analyzer, flutter test),
then one quick diff self-review and PR. Focused Dart unit tests cover business
rules, validation, persistence and error paths. Selective widget tests cover
meaningful UI state such as filters and form validation. Do not add tests for
trivial labels, styling, boilerplate or arbitrary coverage thresholds.

No mandatory all-platform Android/iOS/Web E2E, no compulsory separate reviewer,
and no agent-driven exploratory screenshot inspection for routine features.
Integration tests are reserved for real device/platform dependencies,
security/payment/data-loss or explicitly requested acceptance criteria.
Prefer committed executable tests and meaningful assertions, not agent claims.
Only test the platform(s) relevant to that risk. Missing OPTIONAL E2E is
NOT RUN (not required), not a reason to create a Draft PR. A failed REQUIRED
high-risk check keeps the PR Draft.

The optional Web preview utility can serve a compiled Flutter Web app without
Chrome's debug-service connection:

    python3 .flutter-harness/bin/web-preview.py start
    # Optional browser scenario using Playwright
    python3 .flutter-harness/bin/web-preview.py stop

The old verify-e2e.py is available only when an explicitly requested
all-platform scenario needs a completeness checklist. It does not prove
execution independently and is not part of default PR gating.

See docs/verification-policy.md for the concise risk matrix and the lesson
from the filter incident: a task hidden by Completed was wrongly classified
as an unsuccessful add by the agent. Explicit initial state and test
postconditions prevent that class of false failure.

## Models, permissions and verification

OpenCode V2 defaults to **GPT-6 Luna medium** for implementation and focused
final review. Complex planning and focused diagnosis use Luna High; bounded
worker slices use Luna Low. One Medium parent owns orchestration and delivery.
No automatic premium-model escalation; explicit user model selection remains
possible. See the [model routing and safety guide](docs/model-routing.md).
Templates contain no credentials; authorize your provider locally.

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

## OpenCode V2 completion guard

The **delivery guard** plugin is automatically installed under
`.opencode/plugins/delivery-guard`. On a feature request it records the
initial Git state. When OpenCode would normally finish, the experimental V2
`session.hook("experimental.idle")` runs a **read-only** Git/PR check.
If the task stopped at tests or a local edit without a verified PR, the
plugin inserts a continuation into the same session (at most twice).
After two unsuccessful continuations it fails the execution rather than
silently claiming delivery.

The guard **never** pushes, commits, changes files or bypasses push approval.
`verify-pr.sh` now additionally checks that the PR's remote head SHA equals
local HEAD. It does not prove the feature is correct or that a human actually
performed a semantic review; the standard Flutter CI and owner PR review
remain necessary. The plugin uses an **experimental OpenCode V2 hook** and
must be tested on the Mac with the installed OpenCode version before its
runtime reliability can be claimed. This is a deliberately small delivery
backstop, not a general-purpose background orchestration daemon.

```sh
node --test scripts/test_delivery_guard.mjs
bash .flutter-harness/bin/verify-pr.sh . app
```

## Default short-prompt workflow

1. Ask for a feature using plain language. The agent resolves minor technical
   details independently and asks only material product/security questions.
2. Implement on a feature branch without repetitive planning or worktree gates.
3. Add only necessary unit/widget tests, run one standard code check and
   inspect the task diff once. Use specialized reviewer/device E2E only for
   genuine risk, not by default. The CI repeats deterministic code checks.
4. Commit and push with the required permission, create/update one PR into
   the integration branch; owner reviews and merges. If a required check or
   material issue is unresolved, keep the PR Draft. Do not claim unrun tests.

This workflow keeps the implementation phase dominant over testing/review and
avoids repeated UI tool debugging on small application features.

OpenCode remains interactive for material decisions and push approvals.
Its configuration may be overridden by an already selected model variant,
so usage should be checked from session exports rather than inferred from
the project default.

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

- This is experimental, not production-ready. The third lab trial exposed a
  false Android failure: an active task was successfully added but remained
  hidden under the Completed filter. Overly broad E2E and reviewer requirements
  inflated task duration. The lean policy removes those default obligations.
- OpenCode agent instructions cannot fully guarantee deterministic behavior.
  The machine-checked layer is the Flutter command runner and lightweight CI.
  Production readiness still needs a sustained sequence of successful,
  low-cost feature deliveries and focused high-risk validation.
- Installer preserves existing project configuration and does not automatically
  merge it; synchronize skill/AGENTS changes into each existing project.
- Existing-project adoption and migrations remain out of scope for v0.
- Lab main remains the untouched SDK starter; app is the mutable feature branch.

## Lightweight CI and local device checks

Hosted CI only validates shell syntax, config, installation and fast Python tests.
Android/iOS Maestro and Web Playwright E2E are optional risk-based checks,
not routine CI jobs or prerequisites for every feature.

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

The lab CI fixture omits Web compilation from routine PR checks; optional
full Web/Android/iOS builds remain available **locally** through
`bash .flutter-harness/bin/check.sh . full mobile-web`.

After an approved `git push` and `gh pr create`, the agent checks delivery
with `bash .flutter-harness/bin/verify-pr.sh . app` (or the documented
integration branch). It is read-only and returns BLOCKED if the PR is
missing, closed or targets the wrong base; it never bypasses push approval.

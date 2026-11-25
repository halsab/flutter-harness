# Flutter Harness

Deterministic-first engineering for Flutter Android, iOS and optional Web.
The agent interprets requirements, designs, implements and diagnoses.
Existing CLI/SDK and small scripts execute known operations. No Skills or
MCP enabled by default; one parent model, risk-triggered review only.

**Status: experimental.** This revision requires two live Lab trials on the
owner's installed OpenCode V2. CI and mocked tools cannot prove runtime or
visual reliability. Owner alone accepts/merges PRs.

## Setup and synchronization

Requires Git, Python 3, Flutter/Dart, GitHub CLI, OpenCode V2, and only the
device/browser tools relevant to the task. macOS/Xcode is needed for iOS.
Use the official SDK and GitHub authentication; no credentials in config.

Create a new project and automatically wire, verify and commit its baseline:

    python3 scripts/new-project.py /path/to/app my_app dev.example mobile-web main

Configure the remote integration branch before the first task. To install
or update a Flutter project from a clean Harness checkout:

    bash scripts/install.sh /path/to/app mobile-web main

Lab uses integration branch app instead of main. Profile and base are
explicit; schema 2 stores revision and managed content hashes. Re-run the
same installer to sync. It refuses locally modified managed files, retains
unmanaged AGENTS.md text and app source, and never auto-merges. Existing
pre-schema-2 Lab needs a one-time clean, reviewed replacement:

    bash scripts/install.sh /path/to/flutter-harness-lab mobile-web app --adopt

That migration explicitly replaces the managed config/CI/guards and removes
the retired Skill, PR verifier and agent-authored E2E report helper. Review
the Git diff before committing. Older UI profiles must be migrated to
universal or custom Material before application delivery. Git history is
the rollback mechanism, not a parallel runtime. Restart OpenCode after sync.

## Standard task

Installed command prefix: `python3 .flutter-harness/bin/harness.py`.
The managed [AGENTS.md](templates/PROJECT-AGENTS.md) is the compact workflow.
The CLI uses the project's actual configuration, not a model-selected
profile or hard-coded integration branch.

| Command | Deterministic responsibility |
| --- | --- |
| doctor check / deliver / android / ios / web | Required prerequisites |
| begin feature/name | Clean checkout, fetch base, create/reuse named branch |
| status | Actual branch, dirty paths and candidate fingerprint |
| adopt | Copy missing foundation files for semantic migration |
| scaffold tasks models view_models screens | Create only selected feature folders |
| check | Resolve dependencies, format, conventions, analyze, tests, receipt |
| launch android --device ID | Run current app on explicit emulator |
| launch ios --device ID | Run current app on explicit simulator |
| launch web | Build/serve current Web; reuse healthy identical preview |
| capture android final light | Set requested theme and save runtime artifact |
| capture android final dark | Same target, dark appearance |
| e2e android maestro/flows/task.yaml --device ID | Run real scenario, record outcome |
| e2e web e2e/task.spec.ts | Local Playwright test, HARNESS_WEB_URL from preview |
| visual-evidence | Validate current candidate capture receipts |
| stop-preview | Stop managed local Web server |
| deliver | Check evidence, commit selected files, push, create/update/verify PR |
| verify | Read-only PR verification |
| usage | Export recorded OpenCode sessions and summarize actual counters |
| ci | Validate config and run nonmutating standard code gates in CI |

For ordinary work, begin → implement → check → deliver. No compulsory
separate architect, reviewer, device or browser tests. For substantial
visual changes read [DESIGN](templates/product/DESIGN.md); capture populated
actual runtime states and both themes on one representative target. For
material behavior read [BEHAVIOR](templates/product/BEHAVIOR.md), and for
large coupled tasks [ORCHESTRATION](templates/product/ORCHESTRATION.md).
Product defaults: [PRODUCT](templates/product/PRODUCT.md), Material 3,
feature-first MVVM, adaptive system light/dark from Ocean Blue seed.

Before delivery the agent supplies only semantic parameters and explicit
task files in ignored .flutter-harness/work/delivery.json:

    {
      "message": "feat: filter tasks",
      "title": "Filter tasks",
      "body": "Summary and actual verification",
      "files": ["lib/features/tasks/screens/task_list_screen.dart"],
      "review_required": false,
      "required_e2e": []
    }

List every dirty task path, including tests/lockfile if changed. Set
review_required for semantic risk/owner request, and required_e2e to any
platform whose scripted acceptance is required. The plugin independently
adds known risk flags. The exact canonical deliver command requests owner
permission; direct publication commands are not the workflow. The script
fails closed on dirty files outside the list, stale evidence, wrong base,
stale PR head or unsafe branch. A retry after a successful commit/push
does not recreate the commit. Required blocked checks do not publish.

## Verification and limits

Check receipts bind all Git-tracked and nonignored input contents. The
OpenCode plugin records actual check tool outcomes, bounds reviewer/advisor
attempts and uses actual child session verdicts. Screenshots require
semantic inspection; hashes/receipts are not proof of aesthetic quality or
the currently visible app's semantics. Playwright CLI must be installed
locally for Web capture/E2E; no automatic npm download.

The workflow guard is not an adversarial sandbox. Shell wrappers and a
user with repository credentials can bypass local hooks. Protect the
integration branch in GitHub, require CI and owner review. Never auto-merge,
force-push, or publish secrets. Ignored local receipts are not security
credentials. No device E2E is run by hosted CI.

See [architecture](docs/ARCHITECTURE.md), [verification](docs/verification-policy.md)
and [routing](docs/model-routing.md). Lab: https://github.com/halsab/flutter-harness-lab.
Lab main remains the SDK baseline; app is the mutable integration branch.

Evidence informing these choices (not claimed Flutter speedups):
[Harness Engineering](https://arxiv.org/abs/2609.00006),
[Empirical Harness Design](https://arxiv.org/abs/2609.20804),
[Agentless](https://arxiv.org/abs/2407.01489),
[The Complexity Trap](https://arxiv.org/abs/2508.21433),
[Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988),
[SWE-Skills-Bench](https://arxiv.org/abs/2603.15401),
[AI Agents That Matter](https://arxiv.org/abs/2407.01502),
[Why Multi-Agent Systems Fail](https://arxiv.org/abs/2503.13657),
[Anthropic Harness Design](https://www.anthropic.com/research/harness-design-long-running-apps),
[VISTA](https://arxiv.org/abs/2605.26144),
[Demystifying Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

MIT License.

### Delivery recovery and diagnostics

`deliver` is the sole owner-approved publishing command. It reconciles an already published matching PR without another commit, push or PR edit, and writes `delivery-result.json` before reporting PASS. `completion` checks candidate-bound local evidence without a network call; `verify` additionally checks the live PR. If interrupted, retry `deliver` on the unchanged candidate; do not repeat checks. A push with no matching PR may be repeated idempotently. `diagnostics` exports only structured counters (including provider retries and synthetic continuations), lifecycle events and selected receipts from the recorded sessions into `.flutter-harness/work/diagnostics.json`; no raw session messages or credentials are persisted by this command. The idle hook records recovery/completion and session IDs, not a privileged publication action.

### Material UI acceptance

For material visual changes, run `python3 .flutter-harness/bin/harness.py doctor visual` before implementation. Select one working target; a screenshot probe is not a successful app launch. Declare `.flutter-harness/work/visual-plan.json` (platform, fixture, baseline, scenarios with label/kind and Web viewport) per DESIGN.md. Capture each state in both themes using the CLI, optionally with `--scenario` and `--settle`. The quality gate validates exact current evidence before dispatch and binds the independent verdict to image/plan digests as well as source. Two substantive reviews; at most one additional technical recovery. No duplicate unchanged review, no forced PASS. Material component selection and visible selected state are always project defaults.

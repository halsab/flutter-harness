# Flutter Harness

One OpenCode Build agent, ordinary Git branches, Material 3, feature-first MVVM,
adaptive layout, native checks and owner-approved PR delivery.

Prerequisites: Git, Python 3, Flutter/Dart, GitHub CLI and OpenCode; relevant
device/browser SDK when needed. Authenticate GitHub CLI. Run from a clean
checkout of this Harness repository.

## 1. Initialize an empty project repository

```bash
python3 scripts/new-project.py <project-path> <project-name> <organization> <profile> <integration-branch>
```

| Argument | Meaning | Example |
| --- | --- | --- |
| `project-path` | Local directory of your empty repository | `~/Documents/repos/finance` |
| `project-name` | Flutter/Dart package name: lowercase letters, digits and underscores, starting with a letter | `finance` |
| `organization` | Reverse-domain identifier used to generate native application identifiers | `com.mycompany` |
| `profile` | `mobile` = Android and iOS; `mobile-web` = Android, iOS and Web | `mobile-web` |
| `integration-branch` | Git branch into which task PRs are merged | `main` |

The angle brackets denote placeholders; do not type them literally. Example (replace values with your own):

```bash
python3 scripts/new-project.py ~/Documents/repos/finance finance com.mycompany mobile-web main
```

The package name is not necessarily the user-visible app name; configure the display name separately if needed.

Creates Flutter, installs Harness, checks and commits the starter. The target
may be an empty directory or an existing empty Git repository on the requested
integration branch. Untracked macOS `.DS_Store` metadata is ignored and never
committed. Existing Git history and remote are preserved. Other existing
files or pending tracked changes are reported rather than overwritten.
Publish the initial integration branch before starting OpenCode.

## 2. Install or update Harness in an existing Flutter project

```bash
bash scripts/install.sh <project-path> <profile> <integration-branch>
```

Use the same argument definitions above; the project must already contain a Flutter `pubspec.yaml`. The existing app name and organization are retained.

Example:

```bash
bash scripts/install.sh ~/Documents/repos/finance mobile-web main
```

Preserves app source and unmanaged instructions. Review and commit the managed
changes into integration before starting a fresh session. Existing apps may
require explicit product-standard migration; sync does not rewrite them.

Use `mobile` for Android/iOS only, or `mobile-web` to include Web. Replace
`main` with the actual integration branch. Open OpenCode in the project
directory, select Build / Luna Medium and give one product task. The agent
handles branching, implementation, focused impact checks, source-first review and PR creation; you approve publication and merge. Ordinary text/style/size fixes need no simulator, screenshots or Maestro/Playwright. For material UI inspect the affected final runtime only when cheaper evidence is insufficient. Automated scenarios are reserved for actual risk or explicit requirements.

### Agent scope

Harness instructions, revision checks, task tracking, recovery, and quality/resource
hooks apply only to the root `build` agent. Select Plan, Ask, Review, or any
other configured agent for ordinary conversation, planning, and independent
analysis without starting or completing a Harness task. Switching away from
Build suspends its task hooks; switching back resumes the existing task.
Build-specific workflow permissions are scoped to Build. Shared repository
publication safeguards and location-level plugin/MCP settings remain in force.

## Engineering evolution

For material behavior, define invariants and verify the original user scenario.
The read-only reviewer uses concrete evidence, not speculative refactoring.
Confirmed reusable Harness gaps are reported to central GitHub Issues by the
installed Reporter; application-specific regressions stay in the app. See
[automatic reporting and on-demand maintenance](docs/evolution-automation.md) and [the evolution and Lab evaluation policy](docs/engineering-evolution.md). No separate API credentials or scheduled coding agent.

### Process accumulated Harness Issues

The Reporter automatically records supported, reusable Harness failures in
[flutter-harness Issues](https://github.com/halsab/flutter-harness/issues)
using existing local GitHub CLI authentication as `halsab`. No separate API
key, paid background agent or scheduled repair workflow is required.

When you want to improve Harness, finish any current work, open the central
Harness repository (not an application repository), and check that the
working tree is clean:

```bash
cd ~/Documents/repos/flutter-harness
git status --short
```

If clean, update and start OpenCode:

```bash
git switch main &&
git pull --ff-only origin main &&
gh auth status &&
opencode
```

Select Build / Luna Medium and give the agent this task:

> Process the accumulated Flutter Harness Issues. Deduplicate and reproduce
> confirmed problems, fix their root causes, add focused regression tests and
> open a PR. Preserve the economical model routing and existing quality
> guarantees. Leave unconfirmed issues open.

The agent follows [the maintenance policy](docs/evolution-automation.md).
Review the proposed PR and merge after CI passes. Then update installed
Harness copies in application repositories using the installer in section 2.
There is no need to analyze each Issue manually.

### Blocked task recovery

A Build agent saves local checkpoints without publication; there is no size-based checkpoint gate. If verification stalls it offers `save-draft` after checkpoint, with your publication approval. The verified draft parks the task, never reports DONE, and permits a different task in the same conversation. To resume, ask Build to use `begin <existing-feature-branch> --resume` (clean branch, compatible installed revision); it uses fresh evidence and can update the existing draft with canonical deliver. One explicit permission-gated review-recovery remains available for an exhausted review budget. Never merge a draft or bypass acceptance.

For explicitly required automated visuals, `visual-plan.json` scenarios may specify `"themes":["light","dark"]`; the default is light only. A screen state can be captured without a script; an interaction state needs a project-local executable scenario. Code review happens first, independently. Ordinary statically verifiable UI changes require neither a plan nor screenshots.

### Local checks versus CI

`python3 .flutter-harness/bin/harness.py check` selects unit/widget tests from changed Dart files and their transitive import/export/part dependents. It compares each slice with the last successful candidate (first slice: task base), formats only changed Dart files, avoids unnecessary dependency resolution and records explicit skipped steps. Dependency/global/uncertain changes can expand to the full suite with a recorded reason. A local PASS is an exact candidate-bound impact receipt, not a claim that every test ran. The generated PR CI still executes the complete standard suite. Native and integration/E2E checks are separate and only required for relevant risks. Run the canonical check after implementation and only after meaningful affected fixes; checkpoint coherent work without requiring a check. No routine full local final run.

### Fast CI for Harness itself

Every Harness PR and push to `main` runs the SDK-free Bash, Node, Python, configuration and installer checks. The real Flutter starter job runs automatically only when a PR changes starter creation, generated Dart/scaffold templates, or product policy validation; on `main` pushes the fast checks are sufficient to avoid re-running the PR's starter build. Run **Actions → Bootstrap quality → Run workflow** on the desired ref (or `gh workflow run bootstrap.yml --ref <branch>`) to explicitly exercise the real starter, for example after changing Flutter command/SDK contracts or directly changing starter files on `main`. Other PRs skip the SDK job entirely, including cache restore. The workflow cancels superseded runs for the same event/ref. Application PR CI is separate and retains the complete Flutter suite.

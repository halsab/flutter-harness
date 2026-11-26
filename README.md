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
handles branch, checks, relevant review and PR creation; you approve
publication and merge. No initial screenshot unless comparison is needed.

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

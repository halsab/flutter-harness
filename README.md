# Flutter Harness

One OpenCode Build agent, ordinary Git branches, Material 3, feature-first MVVM,
adaptive layout, native checks and owner-approved PR delivery.

Prerequisites: Git, Python 3, Flutter/Dart, GitHub CLI and OpenCode; relevant
device/browser SDK when needed. Authenticate GitHub CLI. Run from a clean
checkout of this Harness repository.

## 1. Initialize an empty project repository

```bash
python3 scripts/new-project.py /path/to/my-app my_app com.example mobile-web main
```

Creates Flutter, installs Harness, checks and commits the starter. The target
may be an empty directory or an existing empty Git repository on the requested
integration branch. Existing Git remote is preserved. Publish the initial
integration branch before starting OpenCode.

## 2. Install or update Harness in an existing Flutter project

```bash
bash scripts/install.sh /path/to/my-app mobile-web main
```

Preserves app source and unmanaged instructions. Review and commit the managed
changes into integration before starting a fresh session. Existing apps may
require explicit product-standard migration; sync does not rewrite them.

Use `mobile` for Android/iOS only, or `mobile-web` to include Web. Replace
`main` with the actual integration branch. Open OpenCode in the project
directory, select Build / Luna Medium and give one product task. The agent
handles branch, checks, relevant review and PR creation; you approve
publication and merge. No initial screenshot unless comparison is needed.

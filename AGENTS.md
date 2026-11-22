# Flutter Harness contributor instructions

This repository contains the harness, not the user's Flutter application.

- Follow the upstream Superpowers workflows. Do not vendor or rewrite Superpowers.
- Prefer official Dart/Flutter tools and reproducible scripts.
- Never claim a test, simulator, build or MCP connection passed without actually running it.
- Never rewrite or delete an existing project's configuration or source during installation.
- Work on a feature branch, commit after verified milestones, and open a pull request. Never auto-merge.
- Approval from the project owner is mandatory before updating accepted golden screenshots.
- Keep secrets, production credentials and private data out of Git, logs and public PRs.
- Mobile is the default profile. Flutter Web is optional.
- Treat a BLOCKED check as not verified; report the exact missing prerequisite.
- The lab project is separate: https://github.com/halsab/flutter-harness-lab.
- Model and permission rules are versioned in both OpenCode profile templates; do not bypass denied tool operations.
- Ask approval before external-directory access or Git pushes; never mistake CLI prompts for GitHub branch protection.

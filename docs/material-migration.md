# Migrating from the Adaptive foundation

This is a reviewed, explicit upgrade, not a side effect of install.sh.
Installation continues to preserve existing project configuration and source.
Do not run a large product redesign in the same task as foundation adoption.

## Configuration-only sync (existing installations)

On a clean feature branch from the fetched integration branch, compare the
current installed versions against the new Harness sources. Sync only the
Harness-owned baseline files below, merging intentional project overrides:

- templates/product/PRODUCT.md -> .flutter-harness/PRODUCT.md
- templates/product/* -> .flutter-harness/templates/product/ (starter files)
- scripts/check-product.py -> .flutter-harness/bin/check-product.py
- skills/flutter-harness/SKILL.md -> .opencode/skills/flutter-harness/SKILL.md
- templates/opencode-<profile>.jsonc -> corresponding local OpenCode config;
  merge model routes and retain authentication, permissions and other user
  settings. All built-in roles now use Luna. Confirm effective routes in a
  fresh OpenCode session; existing sessions may retain old configuration.
- Update only the Flutter Harness marked section in AGENTS.md to match
  scripts/install.sh. Preserve unrelated project instructions.

If product.json is pending, change ui_profile from adaptive/minimal to
universal explicitly and retain status pending. Do not mark active or alter
architecture/schema until actual foundation adoption. For an already-active
legacy project, do not flip profile alone: keep its existing settings and
policy until a focused source migration can remove the alternate UI together
with the profile change. The checker retains legacy profile recognition to
avoid breaking existing active projects.

## Separate source migration

Use init-product.py to fill only missing starter files, inspect existing
source and dependencies, and remove project-specific Cupertino branches and
unused dependencies only if safe. Preserve data, business rules and tests.
Keep the existing Material appearance/behavior as the baseline, with shared
system light/dark theme. Prefer direct SDK Material widgets and shared tokens
over one-off wrappers. Keep ordinary platform interactions. When all source
is migrated set ui_profile to universal and status active; run the standard
checks and required visual inspection on the actual app.

After this focused migration is accepted, design and implement new features
in separate tasks. No automatic Sol escalation, no compulsory UIKit-like
animations, no third-party visual kit for routine tasks.

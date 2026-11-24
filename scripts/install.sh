#!/usr/bin/env bash
# Non-destructive initial Flutter project integration.
set -euo pipefail

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
info() { printf '%s\n' "$*"; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-}"
PROFILE="${2:-mobile}"

[[ -n "$TARGET" ]] || fail "Usage: bash scripts/install.sh /path/to/flutter-project [mobile|mobile-web]"
[[ "$PROFILE" == "mobile" || "$PROFILE" == "mobile-web" ]] || fail "Invalid profile"
[[ -d "$TARGET" ]] || fail "Project directory not found: $TARGET"
TARGET="$(cd "$TARGET" && pwd -P)"
[[ -f "$TARGET/pubspec.yaml" ]] || fail "Missing pubspec.yaml"
grep -Eq '^[[:space:]]*flutter:[[:space:]]*$' "$TARGET/pubspec.yaml" || fail "No Flutter dependency found in pubspec.yaml"
[[ "$ROOT" != "$TARGET" ]] || fail "Harness source is not a target Flutter project"

mkdir -p "$TARGET/.flutter-harness/bin" "$TARGET/.opencode/skills/flutter-harness"
if [[ ! -e "$TARGET/.flutter-harness/bin/maestro.sh" ]]; then
  cp "$ROOT/scripts/maestro.sh" "$TARGET/.flutter-harness/bin/maestro.sh"
  info "Installed portable Maestro launcher."
else
  info "Preserved existing Maestro launcher."
fi

if [[ ! -e "$TARGET/.flutter-harness/bin/check.sh" ]]; then
  cp "$ROOT/scripts/check.sh" "$TARGET/.flutter-harness/bin/check.sh"
  info "Installed reusable local verification runner."
else
  info "Preserved existing verification runner."
fi

if [[ ! -e "$TARGET/.flutter-harness/bin/verify-pr.sh" ]]; then
  cp "$ROOT/scripts/verify-pr.sh" "$TARGET/.flutter-harness/bin/verify-pr.sh"
  info "Installed PR delivery verification."
else
  info "Preserved existing PR verification."
fi

if [[ "$PROFILE" == "mobile-web" && ! -e "$TARGET/.flutter-harness/bin/web-preview.py" ]]; then
  cp "$ROOT/scripts/web-preview.py" "$TARGET/.flutter-harness/bin/web-preview.py"
  info "Installed deterministic Web preview."
fi

if [[ ! -e "$TARGET/.flutter-harness/bin/verify-e2e.py" ]]; then
  cp "$ROOT/scripts/verify-e2e.py" "$TARGET/.flutter-harness/bin/verify-e2e.py"
  info "Installed platform E2E completeness gate."
fi

touch "$TARGET/.gitignore"
for ignored in '/.playwright-mcp/' '/.flutter-harness/verification.json'; do
  if ! grep -Fxq "$ignored" "$TARGET/.gitignore"; then
    printf '%s\n' "$ignored" >> "$TARGET/.gitignore"
  fi
done

# V2 delivery guard resumes a normal agent session if implementation stops
# without an open, up-to-date PR. Existing plugin files are never overwritten.
mkdir -p "$TARGET/.opencode/plugins/delivery-guard"
for name in index.js guard.mjs quality.mjs; do
  if [[ ! -e "$TARGET/.opencode/plugins/delivery-guard/$name" ]]; then
    cp "$ROOT/plugins/delivery-guard/$name" "$TARGET/.opencode/plugins/delivery-guard/$name"
    info "Installed delivery guard $name."
  fi
done

if [[ ! -e "$TARGET/.flutter-harness/config.json" ]]; then
  printf '{\n  "profile": "%s",\n  "source": "https://github.com/halsab/flutter-harness"\n}\n' "$PROFILE" > "$TARGET/.flutter-harness/config.json"
  info "Created .flutter-harness/config.json ($PROFILE)"
else
  info "Preserved existing harness config; check that the profile is correct."
fi

if [[ ! -e "$TARGET/.opencode/skills/flutter-harness/SKILL.md" ]]; then
  cp "$ROOT/skills/flutter-harness/SKILL.md" "$TARGET/.opencode/skills/flutter-harness/SKILL.md"
  info "Installed Flutter Harness skill."
else
  info "Preserved existing project skill."
fi

if [[ ! -e "$TARGET/opencode.json" && ! -e "$TARGET/opencode.jsonc" ]]; then
  cp "$ROOT/templates/opencode-${PROFILE}.jsonc" "$TARGET/opencode.jsonc"
  info "Created lean autonomous OpenCode V2 config with MCP servers."
else
  info "Preserved existing OpenCode config. Merge with templates/opencode-${PROFILE}.jsonc manually."
fi

[[ -e "$TARGET/AGENTS.md" ]] || : > "$TARGET/AGENTS.md"
if ! grep -Fq '<!-- flutter-harness:start -->' "$TARGET/AGENTS.md"; then
  cat >> "$TARGET/AGENTS.md" <<'INSTRUCTIONS'

<!-- flutter-harness:start -->
## Flutter Harness
Project tooling: https://github.com/halsab/flutter-harness
Read .flutter-harness/config.json and load the flutter-harness skill.

User requests describe outcomes; implement with minimal technical approvals.
Use a feature branch from app (Lab) or the documented integration branch.
Preserve unrelated edits, particularly local opencode.jsonc; stage only task files.
Default model: GPT-6 Luna medium. Sol/extra agents only for difficult work.
Format once with dart format lib test, then run one standard check.
Never remove a failing acceptance test to make checks green. Risky persistent
or destructive changes require a successful check and independent reviewer
verdict on the exact candidate before publication.
Write focused unit tests for important logic and widget tests only for stateful
UI behavior. No tests for boilerplate, trivial styling or coverage quotas.
Android/iOS/Web device/browser E2E are NOT required for ordinary features.
Choose a minimal scripted integration check only when platform/critical risk
actually demands it, or the user explicitly requests E2E.
Do not infer a failed save from an item hidden by a selected filter.
If optional E2E is not needed, report NOT RUN (not required), not BLOCKED.
The legacy verify-e2e.py helper is optional, not a delivery gate.
Preflight one task-diff review BEFORE final checks. Match important new
observable behavior to a focused unit/widget test; green old tests are not
evidence for untested sorting/filter interactions. Avoid redundant tests.
Keep main.dart as entrypoint; put growing feature UI/view state in feature
folders with no gratuitous state-management dependency.
One bounded independent read-only reviewer for cross-feature interactions,
security, sensitive data, migration, concurrency, large architecture or
explicit user request. Skip reviewer for trivial changes; no review loops.
The plugin routes reviewer Luna Medium/High/Extra High (xhigh) from diff size
and risk; large changes require review and persistent-data risk uses at least High.
If required checks pass, push with approval and create a normal PR into app.
If a genuinely required check fails or a material finding remains, use Draft.
Never auto-merge or force-push. Respect denied tool actions and golden approvals.
Keep verification concise and report only actual command results.
<!-- flutter-harness:end -->
INSTRUCTIONS
  info "Added project instructions."
else
  info "Preserved existing project instructions."
fi

info "Installation finished. Review 'git diff' before committing."

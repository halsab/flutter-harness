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

mkdir -p "$TARGET/.flutter-harness" "$TARGET/.opencode/skills/flutter-harness"

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
  info "Created OpenCode V2 config with Superpowers and MCP servers."
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
Use Superpowers for planning, execution and review. Work in feature branches,
commit verified milestones, open pull requests; never merge automatically.
Respect OpenCode model routing and permission prompts; do not bypass denied actions.
Only the human can approve updates to golden image baselines.
Report PASS / FAIL / BLOCKED / SKIPPED accurately.
<!-- flutter-harness:end -->
INSTRUCTIONS
  info "Added project instructions."
else
  info "Preserved existing project instructions."
fi

info "Installation finished. Review 'git diff' before committing."

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

mkdir -p "$TARGET/.flutter-harness/templates/product"
# Copy missing product policy, starter and tools; never overwrite project code.
for name in check-product.py init-product.py task-plan.py; do
  if [[ ! -e "$TARGET/.flutter-harness/bin/$name" ]]; then
    cp "$ROOT/scripts/$name" "$TARGET/.flutter-harness/bin/$name"
  fi
done
while IFS= read -r -d '' file; do
  relative="${file#"$ROOT/templates/product/"}"
  destination="$TARGET/.flutter-harness/templates/product/$relative"
  if [[ ! -e "$destination" ]]; then
    mkdir -p "$(dirname "$destination")"
    cp "$file" "$destination"
  fi
done < <(find "$ROOT/templates/product" -type f -print0)
for name in PRODUCT.md product.json; do
  if [[ ! -e "$TARGET/.flutter-harness/$name" ]]; then
    cp "$ROOT/templates/product/$name" "$TARGET/.flutter-harness/$name"
  fi
done

touch "$TARGET/.gitignore"
for ignored in '/.playwright-mcp/' '/.flutter-harness/verification.json' '/.flutter-harness/previews/' '/.flutter-harness/work/'; do
  if ! grep -Fxq "$ignored" "$TARGET/.gitignore"; then
    printf '%s\n' "$ignored" >> "$TARGET/.gitignore"
  fi
done

# V2 delivery guard resumes a normal agent session if implementation stops
# without an open, up-to-date PR. Existing plugin files are never overwritten.
mkdir -p "$TARGET/.opencode/plugins/delivery-guard"
for name in index.js guard.mjs quality.mjs resources.mjs; do
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
Read .flutter-harness/config.json and .flutter-harness/product.json.
In an active product, use this workflow for isolated fixes/routine features.
No skills by default. Use the specific guides below for nonroutine work.
Read .flutter-harness/PRODUCT.md before pending/unknown adoption or meaningful
UI/architecture changes; preserve the adopted baseline. Default feature-first
MVVM, Material 3, Flutter Web. Never disable the product guard. Prefer CLI
and existing scripts for reproducible operations, not agent interpretation.
Avoid reloading unchanged context.

Implement the requested outcome; ask only material product/security questions.
Fetch the integration base (app in Lab); work on a feature branch, preserve
unrelated edits and stage only task files. Luna Medium by default; no routine
subagents. For material changed behavior read the BEHAVIOR.md guide in
.flutter-harness/templates/product/ before code; for substantial visual work
read DESIGN.md; for complex work read ORCHESTRATION.md. Follow its Luna
High planning/diagnosis, Low worker and optional single Sol Medium advisor
rules. One parent owns delivery; no automatic premium escalation.

Inspect the task diff once before final checks; match meaningful new behavior
to focused unit/widget assertions, reusing adequate tests. Never remove a
failing acceptance test to get green CI. No trivial-label/styling tests or
coverage quotas. Format touched Dart files; run one standard check:
bash .flutter-harness/bin/check.sh . standard
The runner resolves the installed profile. Reuse evidence on unchanged candidates; fix the
first actual failure before rerunning. Keep main.dart focused on bootstrap.

Require independent review for interacting behavior, persistent-data
mutations, destructive changes, security, migration, concurrency, substantial
UI/design-system/architecture changes, large diffs or explicit requests.
Follow the plugin's risk/effort, same-candidate and bounded recovery/review
requirements. For persistence, interacting controls, required E2E or review
edge cases, consult the focused flutter-harness skill if additional guidance
is needed. Material UX requires actual rendered inspection per PRODUCT.md.
Device/browser E2E only for relevant platform/critical risk or explicit request;
use known preconditions and scripted postconditions. Hidden filtered data
is not lost data. Optional unrun E2E is NOT RUN, not a Draft blocker.
Legacy verify-e2e.py is not a default gate.

Push with approval; create/update one PR into the integration branch.
Run bash .flutter-harness/bin/verify-pr.sh . BASE (use the actual base).
Claim delivery only for a verified open PR containing local HEAD. Never
auto-merge, force-push or bypass denied actions/required gates.
Unresolved required checks or material findings mean Draft/INCOMPLETE.
Report observed evidence, not guesses.
<!-- flutter-harness:end -->
INSTRUCTIONS
  info "Added project instructions."
else
  info "Preserved existing project instructions."
fi

info "Installation finished. Review 'git diff' before committing."

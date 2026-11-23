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

User requests describe outcomes; handle technical orchestration autonomously.
Ask only material product/architecture/security questions, and seek at most one
design signoff. No second plan approval or execution-mode question.
For sequential tasks, create a feature branch in this checkout from app (lab)
or the project's documented integration branch; no routine worktree prompt.
Preserve unrelated local changes (especially opencode.jsonc); stage task files only.
Use Luna medium by default; Sol medium only for genuinely hard design/diagnosis.
Check actual session model variant in the UI; it can override config defaults.
Use Luna-low explore for broad unfamiliar-code mapping only, not routine searches.
Discover Android and iOS devices; test on a booted iOS Simulator as well as
Android via Maestro, and Web via Playwright on the Web preview URL; never
use flutter run -d chrome as the Playwright server. Builds are not UI tests.
Run platform checks independently. Save local per-platform outcomes and
real tool evidence in .flutter-harness/verification.json. Run verify-e2e.py
before final review/PR; missing platform checks are INCOMPLETE, so use a
DRAFT PR and do not claim delivery DONE.
Check exact intended post-action text; never change an expected value to hide
an input bug. Report Android/iOS/Web with PASS/FAIL/BLOCKED/SKIPPED evidence.
Review the complete task diff against the integration base, including new files.
For read-only reviewer shell, run Git status, merge-base and diff separately;
no chained commands or subshells. Read files with the read tool, not cat.
If the complete diff could not be inspected, review is OPEN, never PASSED.
Require evidence-backed failure scenarios; one full review, one targeted recheck
for material high-risk fixes. Mark unresolved findings OPEN, never PASSED.
Then push and create a PR to the integration
branch, requesting any required tool approval. Never auto-merge or force-push.
Only the owner accepts changed golden baselines. Honor denied tool operations.
Report PASS / FAIL / BLOCKED / SKIPPED accurately and keep updates concise.
<!-- flutter-harness:end -->
INSTRUCTIONS
  info "Added project instructions."
else
  info "Preserved existing project instructions."
fi

info "Installation finished. Review 'git diff' before committing."

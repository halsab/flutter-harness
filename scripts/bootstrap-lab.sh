#!/usr/bin/env bash
# One-time initialization of flutter-harness-lab using the real Flutter SDK.
set -euo pipefail

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
note() { printf '%s\n' "$*"; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:-$(dirname "$ROOT")/flutter-harness-lab}"
REMOTE="https://github.com/halsab/flutter-harness-lab.git"

command -v git >/dev/null || die "Install Git first"
command -v flutter >/dev/null || die "Flutter SDK is missing: https://docs.flutter.dev/install"
[[ -n "$(git config --global user.name || true)" ]] || die "Configure Git: git config --global user.name 'Your Name'"
[[ -n "$(git config --global user.email || true)" ]] || die "Configure Git: git config --global user.email 'you@example.com'"

if [[ ! -d "$DEST/.git" ]]; then
  [[ ! -e "$DEST" || -d "$DEST" ]] || die "Target exists and is not a directory"
  if [[ -d "$DEST" && -n "$(ls -A "$DEST" 2>/dev/null)" ]]; then
    die "Target directory exists and is not empty: $DEST"
  fi
  git clone "$REMOTE" "$DEST"
fi

cd "$DEST"
[[ "$(git remote get-url origin)" == "$REMOTE" || "$(git remote get-url origin)" == "git@github.com:halsab/flutter-harness-lab.git" ]] || die "Unexpected Git origin"
[[ -z "$(git status --porcelain)" ]] || die "Lab worktree is dirty; back up or commit local changes first"
git switch main
git pull --ff-only origin main

if [[ ! -f pubspec.yaml ]]; then
  note "Creating the default Flutter SDK project (Android, iOS, Web)..."
  flutter create --project-name flutter_harness_lab --org dev.halsab --platforms=android,ios,web .
  flutter test
  mkdir -p .github/workflows
  cp "$ROOT/fixtures/lab-base/.github/workflows/flutter.yml" .github/workflows/flutter.yml
  git add -A
  git commit -m "test(lab): generate default Flutter project using SDK"
  git push -u origin main
else
  note "main already contains a Flutter project; not overwriting it."
fi

if git show-ref --verify --quiet refs/heads/app || git ls-remote --exit-code --heads origin app >/dev/null 2>&1; then
  note "app branch already exists; preserving it."
  note "You can now use both lab branches. Check existing app branch content."
  exit 0
fi

note "Creating app branch and applying minimal test fixture..."
git switch -c app
cp "$ROOT/fixtures/lab-app/lib/main.dart" lib/main.dart
cp "$ROOT/fixtures/lab-app/test/widget_test.dart" test/widget_test.dart
mkdir -p .maestro
cp "$ROOT/fixtures/lab-app/.maestro/smoke.yaml" .maestro/smoke.yaml
flutter analyze
flutter test
git add -A
git commit -m "test(lab): add minimal task application and smoke tests"
git push -u origin app

note "SUCCESS: main = SDK default, app = test application."
note "Lab: $DEST"
note "Next: run bash '$ROOT/scripts/install.sh' '$DEST' mobile-web"

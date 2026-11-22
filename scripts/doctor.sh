#!/usr/bin/env bash
# Read-only local prerequisites report for the owner's Mac.
set -u
printf 'Flutter Harness environment report\n'
printf 'Host: %s / %s\n' "$(uname -s)" "$(uname -m)"

for cmd in git flutter dart xcodebuild xcrun adb java maestro opencode npx gh; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf 'FOUND   %-12s %s\n' "$cmd" "$(command -v "$cmd")"
  else
    printf 'MISSING %s\n' "$cmd"
  fi
done

JBR="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
if [[ -x "$JBR/bin/java" ]]; then
  printf '\n== Android Studio bundled Java ==\n'
  "$JBR/bin/java" -version 2>&1
  printf 'For Flutter JDK selection run: bash scripts/setup-java.sh\n'
fi

if command -v flutter >/dev/null 2>&1; then
  printf '\n== flutter --version ==\n'
  flutter --version || true
  printf '\n== flutter doctor -v ==\n'
  flutter doctor -v || true
  printf '\n== flutter devices ==\n'
  flutter devices || true
fi
if command -v xcrun >/dev/null 2>&1; then
  printf '\n== iOS simulators ==\n'
  xcrun simctl list devices available || true
fi
if command -v adb >/dev/null 2>&1; then
  printf '\n== Android devices ==\n'
  adb devices -l || true
fi
if command -v gh >/dev/null 2>&1; then
  printf '\n== GitHub CLI auth ==\n'
  gh auth status || true
fi
printf '\nDo not publish this local report without reviewing it for personal paths/device IDs.\n'

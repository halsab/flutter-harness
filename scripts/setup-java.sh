#!/usr/bin/env bash
# Opt-in: use the JDK bundled with Android Studio for Flutter.
# This changes Flutter's global JDK preference. It does not change macOS JAVA_HOME.
set -euo pipefail

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

command -v flutter >/dev/null 2>&1 || die "Flutter SDK is not on PATH"
JDK="${1:-/Applications/Android Studio.app/Contents/jbr/Contents/Home}"
[[ -x "$JDK/bin/java" ]] || die "JDK not found at $JDK. Pass its actual home directory as the first argument."

printf 'Selected JDK: %s\n' "$JDK"
"$JDK/bin/java" -version
printf '\nConfiguring Flutter to use this JDK (global Flutter setting).\n'
flutter config --jdk-dir="$JDK"
printf '\nRunning Flutter doctor...\n'
flutter doctor -v
printf '\nNote: the Android build must still be verified against its Gradle wrapper version.\n'
printf 'Java 25 requires Gradle 9.1 or later to RUN Gradle.\n'
printf 'For a generated project: grep distributionUrl android/gradle/wrapper/gradle-wrapper.properties\n'

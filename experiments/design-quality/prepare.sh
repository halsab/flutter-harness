#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: bash experiments/design-quality/prepare.sh NEW_DIRECTORY [tasks|transactions]" >&2
  exit 2
fi
source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$source_dir/../.." && pwd)"
dest="$1"
case_name="${2:-tasks}"
case "$case_name" in tasks|transactions) ;; *) echo "Unknown case: $case_name" >&2; exit 2;; esac
# Never overwrite an existing run, and keep outputs outside the real Flutter app.
if [[ -e "$dest" || -L "$dest" ]]; then
  echo "Destination already exists; choose a new directory." >&2
  exit 1
fi
mkdir -p "$dest"
for candidate in A B; do
  run="$dest/$candidate"
  mkdir -p "$run/.opencode/skills/product-design" "$run/references" "$run/output"
  cp "$repo_root/skills/product-design/SKILL.md" "$run/.opencode/skills/product-design/SKILL.md"
  cp "$source_dir/briefs/$case_name.md" "$run/BRIEF.md"
  cp "$source_dir/RUN.md" "$source_dir/render.sh" "$run/"
  cp "$source_dir/references/"* "$run/references/"
  # Avoid known interactive Superpowers workflow in the standalone experiment.
  printf '%s\n' '{"plugins":["-superpowers","-superpowers.*","-superpowers@git+https://github.com/obra/superpowers.git#v7.0.2"]}' > "$run/opencode.jsonc"
done
mkdir -p "$dest/judge"
cp "$source_dir/briefs/$case_name.md" "$dest/judge/BRIEF.md"
cp "$source_dir/JUDGE.md" "$dest/judge/"
echo "Prepared: $dest/A, $dest/B, $dest/judge"

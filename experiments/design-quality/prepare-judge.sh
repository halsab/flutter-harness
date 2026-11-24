#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 4 ]]; then
  echo 'Usage: bash prepare-judge.sh TASKS_RUN FINANCE_RUN LEGACY_IOS_PNG NEW_DIRECTORY' >&2
  exit 2
fi
source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tasks="$1"; finance="$2"; legacy="$3"; dest="$4"
if [[ -e "$dest" || -L "$dest" ]]; then
  echo 'Destination exists; choose a new directory.' >&2
  exit 1
fi
# Validate everything before making the destination.
for run in "$tasks" "$finance"; do
  for author in A B; do
    for file in concept-1.png concept-2.png handoff.md; do
      test -s "$run/$author/output/$file" || { echo "Missing: $run/$author/output/$file" >&2; exit 1; }
    done
  done
done
test -s "$legacy" || { echo "Missing: $legacy" >&2; exit 1; }
mkdir -p "$dest/visual/tasks" "$dest/visual/finance" "$dest/handoffs/tasks" "$dest/handoffs/finance" "$dest/briefs" "$dest/practice"
copy_candidate() {
  local run="$1" case_name="$2" author="$3" label="$4"
  cp "$run/$author/output/concept-1.png" "$dest/visual/$case_name/$label-1.png"
  cp "$run/$author/output/concept-2.png" "$dest/visual/$case_name/$label-2.png"
  cp "$run/$author/output/handoff.md" "$dest/handoffs/$case_name/$label.md"
}
# Labels intentionally differ across cases. Keep the mapping outside the judge workspace.
copy_candidate "$tasks" tasks A X
copy_candidate "$tasks" tasks B Y
copy_candidate "$finance" finance B X
copy_candidate "$finance" finance A Y
cp "$legacy" "$dest/visual/tasks/legacy.png"
cp "$source_dir/briefs/tasks.md" "$dest/briefs/tasks.md"
cp "$source_dir/briefs/transactions.md" "$dest/briefs/finance.md"
cp "$source_dir/JUDGE-RUN.md" "$dest/RUN.md"
printf '%s\n' '{"plugins":["-superpowers","-superpowers.*","-superpowers@git+https://github.com/obra/superpowers.git#v7.0.2"]}' > "$dest/opencode.jsonc"
for example in appointments-a appointments-b; do
  bash "$source_dir/render.sh" "$source_dir/references/$example.svg" "$dest/practice/$example.png"
done
printf 'Judge workspace: %s\n' "$dest"

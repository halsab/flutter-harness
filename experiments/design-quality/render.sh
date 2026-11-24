#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 2 ]]; then
  echo "Usage: bash render.sh input.svg output.png" >&2
  exit 2
fi
# Reuse installed Chrome; the screenshot CLI may fetch Playwright via npm on
# first use. This is a static concept renderer, not a product web stack.
uri="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve(strict=True).as_uri())' "$1")"
mkdir -p "$(dirname "$2")"
npx --yes playwright screenshot --channel chrome --viewport-size "390,844" "$uri" "$2"
test -s "$2"
python3 - "$2" <<'PY'
import struct, sys
with open(sys.argv[1], "rb") as f:
    header = f.read(24)
if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", header[16:24]) != (390, 844):
    raise SystemExit("Expected a 390 x 844 PNG")
PY

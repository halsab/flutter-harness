#!/usr/bin/env bash
# One installer/synchronizer; explicit profile and integration branch.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/scripts/install.py" "$@"

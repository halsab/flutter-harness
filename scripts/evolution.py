#!/usr/bin/env python3
"""Validate owner reports and restrict the automated patch publication boundary."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

import reporter

# Only fixed descriptions enter the model prompt, never issue/PR/user text.
SCENARIOS = {
    "REPO_RESPONSE": "Investigate invalid canonical GitHub repository response handling.",
    "PR_RESPONSE": "Investigate invalid GitHub pull request response handling.",
    "PR_IDENTITY_MISMATCH": "Investigate canonical PR identity reconciliation.",
    "PR_URL_MISMATCH": "Investigate canonical pull request URL validation, including repository rename.",
    "RISK_CLASSIFICATION": "Investigate reusable risk-classification inconsistencies.",
    "REVIEW_EVIDENCE": "Investigate incorrect review evidence or verdict gating.",
    "BUILD_SCOPE": "Investigate root Build versus non-Build workflow scope.",
    "RUNTIME_EVIDENCE": "Investigate runtime evidence receipt consistency.",
    "DELIVERY_RECONCILIATION": "Investigate delivery retry/reconciliation invariants.",
    "INSTALLER_INVARIANT": "Investigate managed installer invariants.",
}


def accept(issue):
    if (not isinstance(issue, dict) or issue.get("state") != "open" or issue.get("pull_request")
            or issue.get("user", {}).get("login") != reporter.OWNER):
        raise ValueError("Not an open owner report")
    data = reporter.validate(json.loads(issue.get("body", "")))
    if issue.get("title") != reporter.title(data) or issue["body"] != reporter.body(data):
        raise ValueError("Noncanonical report")
    return data


def prompt(data):
    data = reporter.validate(data)
    return ("Investigate the following unconfirmed Harness report, not an app bug.\n"
            + SCENARIOS[data["code"]] + "\nReported revision: " + data["revision"] + "\n"
            "Read AGENTS.md and the relevant source. Establish an exact reproducible failure on current main. "
            "If no defect can be reproduced, leave the checkout unchanged. Otherwise add a focused regression "
            "test that fails before the fix, implement the smallest root-cause correction, and run existing "
            "tests. Preserve all gates, permissions and owner approval. No workflow edits, secrets, external "
            "project access, publishing or unrelated changes. Never invent evidence or change tests merely "
            "to pass. Only modify scripts/, plugins/delivery-guard/, templates/ or docs/. Do not commit.\n")


def git(*args):
    return subprocess.check_output(["git", *args])


def validate_staged():
    # All names originate from Git, never shell interpolation.
    changed = git("diff", "--cached", "--name-only", "-z").decode().split("\0")
    changed = [name for name in changed if name]
    allowed = ("scripts/", "plugins/delivery-guard/", "templates/", "docs/")
    if not changed or len(changed) > 12 or any(not name.startswith(allowed) for name in changed):
        raise ValueError("Patch is empty, oversized or outside permitted paths")
    if not any(re.fullmatch(r"scripts/test_[^/]+\.(?:py|mjs)", name) for name in changed):
        raise ValueError("Regression test required")
    raw = git("diff", "--cached", "--raw", "--no-renames").decode().splitlines()
    for line in raw:
        old, new = line.split()[:2]
        if old not in (":000000", ":100644", ":100755") or new not in ("100644", "100755"):
            raise ValueError("Deletion, symlink or special mode not allowed")
        if old != ":000000" and old[1:] != new:
            raise ValueError("Mode change not allowed")
        if old == ":000000" and new != "100644":
            raise ValueError("New executable not allowed")
    stat = git("diff", "--cached", "--numstat").decode().splitlines()
    total = 0
    for line in stat:
        added, removed, _ = line.split("\t", 2)
        total += int(added) + int(removed)
    if total > 500:
        raise ValueError("Patch exceeds 500 changed lines")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("issue", type=Path)
    prepare.add_argument("output", type=Path)
    sub.add_parser("validate-patch")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            args.output.write_text(prompt(accept(json.loads(args.issue.read_text()))))
        else:
            validate_staged()
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as exc:
        print("Evolution blocked: " + type(exc).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

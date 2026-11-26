#!/usr/bin/env python3
"""Validate owner reports and restrict the automated patch publication boundary."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

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


ATTEMPTED = "harness-evolution-attempted"


def select_issue(pages, requested=None):
    """Select one unattempted canonical issue; skip duplicates even across machines."""
    issues = [item for page in pages for item in page]
    candidates, excluded = [], set()
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        # Closed canonical issues and attempted reports suppress identical reports.
        try:
            data = accept({**issue, "state": "open"})
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
        identity = reporter.key(data)
        if issue.get("state") == "closed" or any(
                label.get("name") == ATTEMPTED for label in issue.get("labels", [])):
            excluded.add(identity)
            continue
        number = issue.get("number")
        if issue.get("state") == "open" and type(number) is int and number > 0:
            candidates.append((number, identity, data))
    for number, identity, data in sorted(candidates, key=lambda item: item[0]):
        if identity not in excluded and (requested is None or requested == number):
            return number, data
    return None


def prompt(data):
    data = reporter.validate(data)
    return ("Investigate the following unconfirmed Harness report, not an app bug.\n"
            + SCENARIOS[data["code"]] + "\nReported revision: " + data["revision"] + "\nDelivery stage: " + data["stage"] + "\n"
            "Read AGENTS.md; inspect only the implicated component and its existing tests. Establish an exact reproducible failure on current main. Stop without a patch if the signal is insufficient; no broad audit, extra agents or model escalation. "
            "If no defect can be reproduced, leave the checkout unchanged. Otherwise add a focused regression "
            "test that fails before the fix, without deleting or replacing any existing test lines. For Node use an existing test suite; new Python test files are also supported. Implement the smallest root-cause correction and run existing "
            "tests. Preserve all gates, permissions and owner approval. No workflow edits, secrets, external "
            "project access, publishing or unrelated changes. Never invent evidence or change tests merely "
            "to pass. Only modify scripts/, plugins/delivery-guard/, templates/ or docs/. Do not commit.\n")


def git(*args):
    return subprocess.check_output(["git", *args])


NODE_TESTS = {"scripts/test_delivery_guard.mjs", "scripts/test_quality_gate.mjs", "scripts/test_resources.mjs"}


def regression_test(name):
    return name in NODE_TESTS or re.fullmatch(r"scripts/test_[A-Za-z0-9_]+\.py", name) is not None


def validate_staged():
    # All names originate from Git, never shell interpolation.
    changed = git("diff", "--cached", "--name-only", "-z").decode().split("\0")
    changed = [name for name in changed if name]
    allowed = ("scripts/", "plugins/delivery-guard/", "templates/", "docs/")
    if not changed or len(changed) > 12 or any(not name.startswith(allowed) for name in changed):
        raise ValueError("Patch is empty, oversized or outside permitted paths")
    tests = [name for name in changed if regression_test(name)]
    if not tests:
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
        added, removed, name = line.split("\t", 2)
        if name in tests and (int(removed) != 0 or int(added) == 0):
            raise ValueError("Automated regression protection must add tests without removing existing lines")
        total += int(added) + int(removed)
    if total > 500:
        raise ValueError("Patch exceeds 500 changed lines")
    return tests


def test_result(root, name):
    command = ([sys.executable, "-m", "unittest", "discover", "-s", "scripts", "-p", Path(name).name]
               if name.endswith(".py") else ["node", "--test", name])
    return subprocess.run(command, cwd=root, timeout=150).returncode


def prove_regression():
    """Run unchanged tests, then the added tests against the exact unpatched source."""
    tests = validate_staged()
    patch = git("diff", "--cached", "--binary", "--", *tests)
    with tempfile.TemporaryDirectory(prefix="harness-regression-") as directory:
        baseline = Path(directory) / "base"
        subprocess.run(["git", "worktree", "add", "--detach", str(baseline), "HEAD"], check=True)
        try:
            for name in tests:
                if (baseline / name).is_file() and test_result(baseline, name) != 0:
                    raise ValueError("Original test suite already fails; cannot prove new regression")
            subprocess.run(["git", "apply", "--index", "-"], cwd=baseline, input=patch, check=True)
            subprocess.run(["git", "-c", "user.name=Harness", "-c", "user.email=harness@example.invalid",
                            "-c", "core.hooksPath=/dev/null", "commit", "-m", "regression tests only"],
                           cwd=baseline, check=True)
            results = [test_result(baseline, name) for name in tests]
            if any(result not in (0, 1) for result in results) or 1 not in results:
                raise ValueError("New tests did not expose a failing scenario on original source")
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(baseline)], check=True)
    print("PASS regression: original tests passed; new tests fail on original source")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("issue", type=Path)
    prepare.add_argument("output", type=Path)
    select = sub.add_parser("select")
    select.add_argument("issues", type=Path)
    select.add_argument("output", type=Path)
    select.add_argument("--number", type=int)
    sub.add_parser("validate-patch")
    sub.add_parser("prove-regression")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            args.output.write_text(prompt(accept(json.loads(args.issue.read_text()))))
        elif args.command == "select":
            selection = select_issue(json.loads(args.issues.read_text()), args.number)
            if selection:
                number, data = selection
                args.output.write_text(prompt(data))
                print(number)
        elif args.command == "prove-regression":
            prove_regression()
        else:
            validate_staged()
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as exc:
        print("Evolution blocked: " + type(exc).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

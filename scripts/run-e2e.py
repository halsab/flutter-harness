#!/usr/bin/env python3
"""Run real Flutter integration tests on devices and Playwright tests on Web.

Feature tests are project-owned and committed. Run from the Flutter project root:
 python3 .flutter-harness/bin/run-e2e.py --mobile-test integration_test/feature_test.dart \
   --android-device emulator-5554 --ios-device SIMULATOR_UDID \
   --web-test e2e/feature.spec.ts

The harness executes each platform independently, records exit codes and hashed
logs in ~/.cache/flutter-harness, and writes a local verification.json report.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

from importlib.machinery import SourceFileLoader


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def source_digest(root):
    """Fingerprint the source and test inputs without depending on git commits."""
    digest = hashlib.sha256()
    paths = [root / name for name in ("pubspec.yaml", "pubspec.lock")]
    directories = ("lib", "test", "integration_test", "e2e", "assets", "android", "ios", "web")
    ignore = {"build", ".dart_tool", ".gradle", "Pods", ".symlinks", ".git", "node_modules"}
    for name in directories:
        directory = root / name
        if directory.is_dir():
            paths.extend(p for p in directory.rglob("*") if p.is_file()
                         and not p.is_symlink() and not any(part in ignore for part in p.relative_to(root).parts))
    for path in sorted((p for p in paths if p.is_file() and not p.is_symlink()), key=str):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode() + b"\0")
        digest.update(sha256(path.read_bytes()).encode() + b"\n")
    return digest.hexdigest()


def in_project(root, value, directory, suffixes):
    if not value:
        return None
    path = (root / value).resolve()
    if not path.is_relative_to(root / directory) or not path.is_file():
        return None
    if not any(path.name.endswith(extension) for extension in suffixes):
        return None
    return path


def log_result(root, run_dir, platform, target, tool, scenario, status,
               reason="", exit_code=None, started=None, duration=0):
    log = run_dir / (platform + ".log")
    if not log.exists():
        log.write_text(reason + "\n", encoding="utf-8")
    return {
        "status": status, "target": target or "", "tool": tool,
        "scenario": str(scenario.relative_to(root)) if scenario else "",
        "scenario_sha256": sha256(scenario.read_bytes()) if scenario else "",
        "exit_code": exit_code, "reason": reason,
        "log": str(log.resolve()), "log_sha256": sha256(log.read_bytes()),
        "started_at": started or dt.datetime.now(dt.timezone.utc).isoformat(),
        "duration_seconds": round(duration, 2),
    }


def execute(command, root, log_path, timeout, env=None):
    before = time.monotonic()
    with log_path.open("w", encoding="utf-8") as log:
        log.write("HARNESS COMMAND (argv, no shell): " + json.dumps(command) + "\n")
        log.flush()
        try:
            done = subprocess.run(command, cwd=root, env=env, stdout=log,
                                  stderr=subprocess.STDOUT, timeout=timeout, check=False)
            return done.returncode, "", time.monotonic() - before
        except subprocess.TimeoutExpired:
            return 124, f"Command timed out after {timeout}s", time.monotonic() - before
        except OSError as exc:
            return 127, f"Unable to start process: {exc}", time.monotonic() - before


def devices(root):
    try:
        result = subprocess.run(["flutter", "devices", "--machine"], cwd=root,
                                capture_output=True, text=True, timeout=40, check=False)
        if result.returncode:
            return [], result.stderr.strip() or "flutter devices failed"
        return json.loads(result.stdout), ""
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        return [], str(exc)


def device_match(found, target, platform):
    for device in found:
        if device.get("id") != target:
            continue
        kind = str(device.get("targetPlatform", "")).lower()
        if platform == "android" and "android" in kind:
            return True
        if platform == "ios" and kind == "ios" and device.get("emulator") is True:
            return True
    return False


def run_mobile(root, run_dir, platform, target, scenario, detected, diagnostic, timeout):
    tool = "flutter-integration"
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    log = run_dir / (platform + ".log")
    if not scenario:
        return log_result(root, run_dir, platform, target, tool, None,
                          "BLOCKED", "Missing committed integration_test/*.dart scenario")
    if not target:
        return log_result(root, run_dir, platform, target, tool, scenario,
                          "BLOCKED", "Explicit device ID required")
    if diagnostic or not device_match(detected, target, platform):
        return log_result(root, run_dir, platform, target, tool, scenario,
                          "BLOCKED", "Target not available as a running " + platform +
                          (" simulator: " + diagnostic if diagnostic else " device"))
    command = ["flutter", "test", str(scenario.relative_to(root)), "-d", target,
               "--reporter", "expanded"]
    code, reason, duration = execute(command, root, log, timeout)
    return log_result(root, run_dir, platform, target, tool, scenario,
                      "PASS" if code == 0 else "FAIL", reason or
                      ("" if code == 0 else "Integration test exit " + str(code)),
                      code, start, duration)


def run_web(root, run_dir, scenario, timeout):
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    log = run_dir / "web.log"
    tool = "playwright-cli"
    if not scenario:
        return log_result(root, run_dir, "web", "", tool, None,
                          "BLOCKED", "Missing committed e2e/*.spec.ts or *.spec.js test")
    binary = root / "node_modules" / ".bin" / "playwright"
    if not binary.is_file():
        return log_result(root, run_dir, "web", "", tool, scenario,
                          "BLOCKED", "Install project-pinned @playwright/test first (npm ci)")
    preview = root / ".flutter-harness" / "bin" / "web-preview.py"
    if not preview.is_file():
        return log_result(root, run_dir, "web", "", tool, scenario,
                          "BLOCKED", "Missing web-preview.py")
    startup = subprocess.run([sys.executable, str(preview), "start"], cwd=root,
                             capture_output=True, text=True, timeout=450, check=False)
    url_match = re.search(r"READY Web URL: (http://127\.0\.0\.1:\d+/)", startup.stdout)
    if startup.returncode or not url_match:
        log.write_text(startup.stdout + "\n" + startup.stderr, encoding="utf-8")
        return log_result(root, run_dir, "web", "", tool, scenario, "FAIL",
                          "Web preview failed; see log", startup.returncode or 1, start)
    url = url_match.group(1)
    env = dict(os.environ, HARNESS_WEB_URL=url)
    try:
        cmd = [str(binary), "test", str(scenario.relative_to(root)),
               "--workers=1", "--reporter=line"]
        code, reason, duration = execute(cmd, root, log, timeout, env=env)
    finally:
        subprocess.run([sys.executable, str(preview), "stop"], cwd=root,
                       capture_output=True, text=True, timeout=20, check=False)
    return log_result(root, run_dir, "web", url, tool, scenario,
                      "PASS" if code == 0 else "FAIL", reason or
                      ("" if code == 0 else "Playwright exit " + str(code)),
                      code, start, duration)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("mobile", "mobile-web"), default="mobile-web")
    parser.add_argument("--mobile-test", required=True)
    parser.add_argument("--android-device", required=True)
    parser.add_argument("--ios-device", required=True)
    parser.add_argument("--web-test")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--output", default=".flutter-harness/verification.json")
    args = parser.parse_args(argv)
    root = Path.cwd().resolve()
    if not (root / "pubspec.yaml").is_file():
        parser.error("Run from Flutter project root")
    if not (30 <= args.timeout <= 1800):
        parser.error("Timeout must be between 30 and 1800 seconds")
    output = (root / args.output).resolve()
    if not output.is_relative_to(root / ".flutter-harness"):
        parser.error("Report must be under .flutter-harness/")
    mobile = in_project(root, args.mobile_test, "integration_test", (".dart",))
    web = in_project(root, args.web_test, "e2e", (".spec.ts", ".spec.js"))
    run_dir = (Path.home() / ".cache" / "flutter-harness" / root.name /
               "e2e" / (dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") +
                        "-" + uuid.uuid4().hex[:8]))
    run_dir.mkdir(parents=True, exist_ok=True)
    found, diagnostic = devices(root)
    result = {}
    for platform, target in (("android", args.android_device), ("ios", args.ios_device)):
        result[platform] = run_mobile(root, run_dir, platform, target, mobile,
                                      found, diagnostic, args.timeout)
        print(platform.upper() + ": " + result[platform]["status"], flush=True)
    if args.profile == "mobile-web":
        result["web"] = run_web(root, run_dir, web, args.timeout)
        print("WEB: " + result["web"]["status"], flush=True)
    report = {
        "schema": 2, "origin": "harness-run-e2e",
        "profile": args.profile, "source_digest": source_digest(root),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "results": result,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("Evidence: " + str(output))
    return 0 if all(row["status"] == "PASS" for row in result.values()) else 3


if __name__ == "__main__":
    sys.exit(main())

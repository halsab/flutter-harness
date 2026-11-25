"""Exercise profile resolution and check order without Flutter or model calls."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

RUNNER = Path(__file__).resolve().with_name("check.sh")


class CheckProfileTest(unittest.TestCase):
    def run_check(self, config=None, args=("full","mobile"), dart_status=0, flutter_body=None, suite_timeout="180"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "app"
            project.mkdir()
            (project / "pubspec.yaml").touch()
            if config is not None:
                (project / ".flutter-harness").mkdir()
                (project / ".flutter-harness/config.json").write_text(config)
            fakebin = root / "bin"
            fakebin.mkdir()
            for name, body in {
                "dart": f'echo "dart $*" >> "$CALLS"\nexit {dart_status}',
                "flutter": flutter_body or 'echo "flutter $*" >> "$CALLS"',
                "uname": "echo Darwin",
            }.items():
                path = fakebin / name
                path.write_text("#!/bin/sh\n" + body + "\n")
                path.chmod(0o755)
            calls = root / "calls"
            env = dict(os.environ, PATH=f"{fakebin}:{os.environ['PATH']}",
                       CALLS=str(calls), HARNESS_ARTIFACTS_DIR=str(root / "logs"),HARNESS_TEST_SUITE_TIMEOUT=suite_timeout)
            result = subprocess.run(["bash", str(RUNNER), str(project), *args],
                                    env=env, capture_output=True, text=True, timeout=10)
            return result, calls.read_text().splitlines() if calls.exists() else []

    def test_explicit_internal_profile(self):
        for profile, web in [("mobile-web", True), ("mobile", False)]:
            with self.subTest(profile=profile):
                result, calls = self.run_check(args=("full", profile))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(calls[:3], ["dart format --output=none --set-exit-if-changed lib test",
                                             "flutter analyze", "flutter test --fail-fast --timeout 45s --reporter expanded"])
                self.assertEqual(calls[3:], ["flutter build apk --debug",
                                             "flutter build ios --simulator --no-codesign"] +
                                 (["flutter build web"] if web else []))

    def test_fail_fast_skips_tests_after_analyze_failure(self):
        result,calls=self.run_check(flutter_body='echo "flutter $*" >> "$CALLS"\nexit 1')
        self.assertEqual(result.returncode,1)
        self.assertEqual(calls[-1],"flutter analyze")
        self.assertIn("FAIL analyze",result.stdout)

    def test_timeout_kills_hung_step_and_reports_failure(self):
        result,calls=self.run_check(args=("standard","mobile"),suite_timeout="1",
            flutter_body='echo "flutter $*" >> "$CALLS"\nif [ "$1" = test ]; then echo "test stuck"; sleep 60; fi')
        self.assertEqual(result.returncode,1)
        self.assertIn("TIMEOUT flutter-tests",result.stdout)
        self.assertIn("test stuck",result.stdout)
        self.assertNotIn("PASS flutter-tests",result.stdout)

    def test_missing_or_invalid_internal_profile(self):
        for args in (("full",), ("full", "desktop")):
            result, calls = self.run_check(args=args)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(calls, [])

    def test_standard_and_format_failure(self):
        config = '{"profile":"mobile-web"}'
        result, calls = self.run_check(config, ("standard","mobile-web"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[1:], ["flutter analyze", "flutter test --fail-fast --timeout 45s --reporter expanded"])
        result, calls = self.run_check(config, ("standard","mobile-web"), dart_status=1)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(calls), 1)
        self.assertIn("FAIL format", result.stdout)


if __name__ == "__main__":
    unittest.main()

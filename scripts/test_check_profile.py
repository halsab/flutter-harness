"""Exercise profile resolution and check order without Flutter or model calls."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

RUNNER = Path(__file__).resolve().with_name("check.sh")


class CheckProfileTest(unittest.TestCase):
    def run_check(self, config=None, args=("full",), dart_status=0):
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
                "flutter": 'echo "flutter $*" >> "$CALLS"',
                "uname": "echo Darwin",
            }.items():
                path = fakebin / name
                path.write_text("#!/bin/sh\n" + body + "\n")
                path.chmod(0o755)
            calls = root / "calls"
            env = dict(os.environ, PATH=f"{fakebin}:{os.environ['PATH']}",
                       CALLS=str(calls), HARNESS_ARTIFACTS_DIR=str(root / "logs"))
            result = subprocess.run(["bash", str(RUNNER), str(project), *args],
                                    env=env, capture_output=True, text=True, timeout=10)
            return result, calls.read_text().splitlines() if calls.exists() else []

    def test_installed_profile_and_explicit_override(self):
        for config, args, web in [
            (json.dumps({"profile": "mobile-web"}), ("full",), True),
            (json.dumps({"profile": "mobile"}), ("full",), False),
            (None, ("full",), False),
            (json.dumps({"profile": "mobile-web"}), ("full", "mobile"), False),
        ]:
            with self.subTest(config=config, args=args):
                result, calls = self.run_check(config, args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(calls[:3], ["dart format --output=none --set-exit-if-changed lib test",
                                             "flutter analyze", "flutter test"])
                self.assertEqual(calls[3:], ["flutter build apk --debug",
                                             "flutter build ios --simulator --no-codesign"] +
                                 (["flutter build web"] if web else []))

    def test_invalid_installed_profile_blocks_before_cli(self):
        for config in ("{", "{}", '{"profile":"desktop"}'):
            with self.subTest(config=config):
                result, calls = self.run_check(config)
                self.assertEqual(result.returncode, 3)
                self.assertIn("BLOCKED", result.stderr)
                self.assertEqual(calls, [])

    def test_standard_and_format_failure(self):
        config = '{"profile":"mobile-web"}'
        result, calls = self.run_check(config, ("standard",))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[1:], ["flutter analyze", "flutter test"])
        result, calls = self.run_check(config, ("standard",), dart_status=1)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(calls), 1)
        self.assertIn("FAIL format", result.stdout)


if __name__ == "__main__":
    unittest.main()

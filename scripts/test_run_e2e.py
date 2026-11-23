"""Unit coverage for source-bound executable platform E2E reports (no devices)."""
import importlib.machinery
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).parent
runner = importlib.machinery.SourceFileLoader("harness_runner", str(HERE / "run-e2e.py")).load_module()
verifier = importlib.machinery.SourceFileLoader("harness_verifier", str(HERE / "verify-e2e.py")).load_module()


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "pubspec.yaml").write_text("name: fixture\n")
        for name in ("integration_test", "e2e"):
            (self.root / name).mkdir()
        (self.root / "integration_test" / "smoke_test.dart").write_text("testWidgets('smoke', () {});")
        (self.root / "e2e" / "smoke.spec.ts").write_text("test('smoke', async () => {});")
        self.digest = runner.source_digest(self.root)
        self.rows = {}
        for name in ("android", "ios", "web"):
            log = self.root / (name + ".log")
            log.write_text("HARNESS COMMAND: test completed\n")
            scenario = self.root / ("e2e/smoke.spec.ts" if name == "web"
                                    else "integration_test/smoke_test.dart")
            self.rows[name] = {
                "status": "PASS", "target": name + "-device", "exit_code": 0,
                "tool": "playwright-cli" if name == "web" else "flutter-integration",
                "scenario": str(scenario.relative_to(self.root)),
                "scenario_sha256": runner.sha256(scenario.read_bytes()),
                "log": str(log), "log_sha256": runner.sha256(log.read_bytes())
            }
        self.report = {
            "schema": 2, "origin": "harness-run-e2e", "profile": "mobile-web",
            "source_digest": self.digest, "results": self.rows
        }

    def verify(self):
        return verifier.verify(self.report, "mobile-web", self.root, runner.source_digest(self.root))

    def test_real_report_shape_passes(self):
        self.assertEqual(self.verify(), [])

    def test_handwritten_old_style_claims_rejected(self):
        self.assertIn("handwritten", " ".join(verifier.verify({"android": {"status": "PASS"}},
                                                            "mobile-web", self.root, self.digest)))

    def test_missing_platform_fails(self):
        del self.rows["ios"]
        self.assertTrue(any("ios" in issue for issue in self.verify()))

    def test_failed_run_cannot_pass(self):
        self.rows["android"]["exit_code"] = 1
        self.assertTrue(any("android" in issue for issue in self.verify()))

    def test_log_tampering_fails(self):
        (self.root / "ios.log").write_text("manually changed")
        self.assertTrue(any("ios" in issue for issue in self.verify()))

    def test_source_edit_invalidates_results(self):
        (self.root / "integration_test" / "smoke_test.dart").write_text("changed")
        self.assertTrue(any("source files changed" in issue for issue in self.verify()))

    def test_scenario_restriction(self):
        self.assertIsNone(runner.in_project(self.root, "../etc/passwd",
                                              "integration_test", (".dart",)))
        self.assertIsNone(runner.in_project(self.root, "e2e/smoke.spec.ts",
                                              "integration_test", (".dart",)))

    def test_platform_device_selection(self):
        devices = [
            {"id": "android-1", "targetPlatform": "android-arm64", "emulator": True},
            {"id": "ios-sim", "targetPlatform": "ios", "emulator": True},
            {"id": "ios-phone", "targetPlatform": "ios", "emulator": False},
        ]
        self.assertTrue(runner.device_match(devices, "android-1", "android"))
        self.assertTrue(runner.device_match(devices, "ios-sim", "ios"))
        self.assertFalse(runner.device_match(devices, "ios-phone", "ios"))


if __name__ == "__main__":
    unittest.main()

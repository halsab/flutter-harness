"""Check the report gate rejects missing platforms and unsupported PASS."""
import runpy
import unittest
from pathlib import Path

verify = runpy.run_path(str(Path(__file__).with_name("verify-e2e.py")))["verify"]


class EvidenceTests(unittest.TestCase):
    def test_missing_platforms(self):
        report = {"android": {"status": "PASS", "target": "emulator", "tool": "maestro",
                              "assertions": "filter", "evidence": "tool call 1"}}
        problems = verify(report, "mobile-web")
        self.assertTrue(any("ios: MISSING" in x for x in problems))
        self.assertTrue(any("web: MISSING" in x for x in problems))

    def test_blocked_and_skipped_are_incomplete(self):
        report = {"android": {"status": "BLOCKED", "reason": "device unavailable"},
                  "ios": {"status": "SKIPPED", "reason": "not tested"},
                  "web": {"status": "FAIL", "reason": "blank page"}}
        self.assertEqual(len(verify(report, "mobile-web")), 3)

    def test_complete_report(self):
        report = {name: {"status": "PASS", "target": "device or url",
                         "tool": "playwright" if name == "web" else "maestro",
                         "assertions": "after action", "evidence": "run id"}
                  for name in ("android", "ios", "web")}
        self.assertEqual(verify(report, "mobile-web"), [])

    def test_empty_pass_is_invalid(self):
        self.assertTrue(verify({n: {"status": "PASS"} for n in ("android", "ios", "web")}, "mobile-web"))


if __name__ == "__main__":
    unittest.main()

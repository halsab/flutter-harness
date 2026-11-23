"""Smoke test deterministic local Web preview; no Flutter SDK/browser needed."""
import contextlib
import io
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

mod = runpy.run_path(str(Path(__file__).with_name("web-preview.py")))


class PreviewTests(unittest.TestCase):
    def test_start_status_stop(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "pubspec.yaml").write_text("name: demo\n")
            web = root / "build" / "web"
            web.mkdir(parents=True)
            (web / "index.html").write_text("<title>preview</title>")
            scripts = root / "bin"
            scripts.mkdir()
            fake_flutter = scripts / "flutter"
            fake_flutter.write_text("#!/bin/sh\nexit 0\n")
            fake_flutter.chmod(0o755)
            with patch.dict(os.environ, {"HOME": td, "PATH": str(scripts) + os.pathsep + os.environ["PATH"]}):
                with patch("pathlib.Path.cwd", return_value=root):
                    with contextlib.redirect_stdout(io.StringIO()) as out:
                        self.assertEqual(mod["main"](["start"]), 0)
                        self.assertEqual(mod["main"](["status"]), 0)
                        self.assertEqual(mod["main"](["stop"]), 0)
                    self.assertIn("READY Web URL:", out.getvalue())
                    self.assertIn("HTTP READY is not E2E PASS", out.getvalue())


if __name__ == "__main__":
    unittest.main()

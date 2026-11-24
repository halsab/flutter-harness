import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

guard = load("check-product")
starter = load("init-product")

class ProductTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write("pubspec.yaml", "name: demo\n")
        self.config("active")
        self.write("lib/main.dart", "import 'app/bootstrap.dart';\nvoid main() => bootstrap();\n")
        self.write("lib/app/bootstrap.dart", "void bootstrap() {}\n")
        self.write("lib/app/app.dart", "")
        self.write("lib/design_system/design_system.dart", "")
        self.write("lib/features/tasks/models/task.dart", "")
        self.write("lib/features/tasks/repositories/tasks.dart", "import '../models/task.dart';")
        self.write("lib/features/tasks/view_models/tasks_vm.dart", "import '../repositories/tasks.dart';")
        self.write("lib/features/tasks/screens/tasks_screen.dart", "import '../view_models/tasks_vm.dart';\nimport 'package:demo/design_system/design_system.dart';")

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def config(self, status, profile="universal"):
        self.write(".flutter-harness/product.json", json.dumps(dict(schema=1, architecture="feature-mvvm", ui_profile=profile, status=status)))

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def test_valid_foundation(self):
        self.assertEqual(guard.verify(self.root), [])

    def test_boundaries_and_styles(self):
        self.write("lib/features/tasks/screens/bad.dart", "import '../repositories/tasks.dart';\nimport 'package:material_ui/material_ui.dart';\nimport 'package:shared_preferences/shared_preferences.dart';\nfinal c = Color(0xFF000000);")
        self.write("lib/features/tasks/view_models/bad.dart", "import '../screens/tasks_screen.dart';\nimport 'package:flutter/widgets.dart';")
        self.write("lib/features/tasks/widgets/other.dart", "import 'package:demo/features/other/models/model.dart';")
        self.write("lib/main.dart", "class MyApp {}")
        errors = "\n".join(guard.verify(self.root))
        for expected in ["main must only call", "invalid feature/layer dependency", "storage/network directly", "fixed palette", "non-view layer must not import UI"]:
            self.assertIn(expected, errors)

    def test_material_direct_in_view_not_domain(self):
        self.write("lib/features/tasks/screens/material.dart", "import 'package:material_ui/material_ui.dart';")
        self.write("lib/app/material.dart", "import 'package:flutter/material.dart';")
        self.assertEqual(guard.verify(self.root), [])
        self.write("lib/features/tasks/models/bad.dart", "import 'package:material_ui/material_ui.dart';")
        self.assertIn("non-view layer must not import UI", "\n".join(guard.verify(self.root)))

    def test_universal_rejects_alternate_ui_even_in_design_system(self):
        self.write("lib/design_system/alternate.dart", "import 'package:cupertino_ui/cupertino_ui.dart';")
        self.assertIn("universal uses Material only", "\n".join(guard.verify(self.root)))
        self.config("active", "adaptive")
        self.assertEqual(guard.verify(self.root), [])

    def test_legacy_boundary_unchanged(self):
        self.config("active", "adaptive")
        self.write("lib/features/tasks/screens/direct.dart", "import 'package:material_ui/material_ui.dart';")
        self.assertIn("platform UI library", "\n".join(guard.verify(self.root)))

    def test_material_starter_defaults(self):
        template = Path(__file__).resolve().parents[1] / "templates/product"
        self.assertEqual(json.loads((template / "product.json").read_text())["ui_profile"], "universal")
        for file in template.rglob("*.dart.template"):
            self.assertNotIn("cupertino_ui", file.read_text())
            self.assertNotIn("usesCupertino", file.read_text())

    def test_comment_and_string_do_not_create_style_violations(self):
        self.write("lib/features/tasks/widgets/comment.dart", "// Colors.red\nfinal text = 'Color(0xFF000000)';\nfinal padding = EdgeInsets.all(AppTokens.space8);")
        self.assertEqual(guard.verify(self.root), [])

    def test_pending_only_for_config_only_adoption_never_downgrade(self):
        self.git("init", "-b", "app")
        self.git("config", "user.name", "Harness")
        self.git("config", "user.email", "test@example.invalid")
        (self.root / ".flutter-harness/product.json").unlink()
        self.git("add", ".")
        self.git("commit", "-m", "legacy")
        self.git("switch", "-c", "adopt")
        self.config("pending")
        self.assertTrue(guard.verify(self.root))
        self.assertEqual(guard.verify(self.root, "app"), [])
        self.write("lib/features/tasks/models/new.dart", "")
        self.assertTrue(guard.verify(self.root, "app"))
        (self.root / "lib/features/tasks/models/new.dart").unlink()
        self.config("active")
        self.git("add", ".")
        self.git("commit", "-m", "active")
        self.git("branch", "-f", "app", "HEAD")
        self.config("pending")
        self.assertTrue(guard.verify(self.root, "app"))

    def test_starter_is_non_destructive(self):
        template = Path(__file__).resolve().parents[1] / "templates/product"
        starter.install(self.root, template)
        path = self.root / "lib/design_system/tokens.dart"
        self.assertIn("AppTokens", path.read_text())
        path.write_text("// customized")
        starter.install(self.root, template)
        self.assertEqual(path.read_text(), "// customized")

if __name__ == "__main__":
    unittest.main()

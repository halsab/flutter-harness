"""Deterministic regression cases for the production impact-check loop."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import check_scope as scope


class Impact(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Harness")
        self.git("config", "user.email", "test@example.invalid")
        self.write(".gitignore", ".dart_tool/\n")
        self.write("pubspec.yaml", "name: demo\n")
        self.write("lib/a.dart", "int a = 1;\n")
        self.write("lib/b.dart", "int b = 1;\n")
        self.write("lib/barrel.dart", "export 'a.dart';\n")
        self.write("test/helper.dart", "import 'package:demo/barrel.dart';\n")
        self.write("test/a_test.dart", "import 'helper.dart';\n")
        self.write("test/b_test.dart", "import '../lib/b.dart';\n")
        self.write(".dart_tool/package_config.json", '{"packages":[]}')
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        self.task = {"base_head": self.git("rev-parse","HEAD").strip(), "branch":"feature", "revision":"fixture"}

    def git(self, *args):
        return subprocess.check_output(["git","-C",str(self.root),*args],stderr=subprocess.PIPE,text=True)

    def write(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(value)

    def plan(self, prior=None):
        return scope.plan(self.root,self.task,prior)

    def test_transitive_selection_and_incremental_after_checkpoint(self):
        self.write("lib/a.dart","int a = 2;\n")
        first, progress = self.plan()
        self.assertEqual(first["mode"],"selected")
        self.assertEqual(first["tests"],["test/a_test.dart"])
        self.assertEqual(first["format"],["lib/a.dart"])
        self.assertFalse(first["pub_get"])
        self.git("add",".")
        self.git("commit","-m","slice A")
        same, _ = self.plan(progress)
        self.assertEqual(same["mode"],"none")
        self.assertFalse(same["analyze"])
        self.write("lib/b.dart","int b = 2;\n")
        second, _ = self.plan(progress)
        self.assertEqual(second["tests"],["test/b_test.dart"])
        self.assertEqual(second["changed"],["lib/b.dart"])

    def test_test_only_and_helper(self):
        self.write("test/b_test.dart","import '../lib/b.dart'; // regression\n")
        p, progress = self.plan()
        self.assertEqual(p["tests"],["test/b_test.dart"])
        self.assertFalse(p["product"])
        self.write("test/helper.dart","import 'package:demo/barrel.dart'; // changed\n")
        p, _ = self.plan(progress)
        self.assertEqual(p["tests"],["test/a_test.dart"])

    def test_native_change_never_runs_unrelated_dart_tests(self):
        self.write("android/app/src/main/AndroidManifest.xml","<manifest/>")
        p, progress = self.plan()
        self.assertEqual(p["mode"],"none")
        self.assertEqual(p["platforms"],["android"])
        self.assertFalse(p["analyze"])
        self.assertFalse(p["product"])
        self.assertFalse(p["pub_get"])
        self.write("test/native_test.dart","import 'dart:io';\n")
        _, progress = self.plan(progress)
        self.write("android/app/src/main/AndroidManifest.xml","<manifest><!-- fixed --></manifest>")
        p, _ = self.plan(progress)
        self.assertEqual(p["tests"],["test/native_test.dart"])

    def test_maestro_edit_does_not_trigger_full_flutter_suite(self):
        self.write("maestro/location.yaml","appId: demo\n---\n- tapOn: Search\n")
        p, _ = self.plan()
        self.assertEqual(p["mode"],"none")
        self.assertFalse(p["pub_get"])
        self.assertFalse(p["analyze"])

    def test_dependency_changes_expand_once(self):
        self.write("pubspec.yaml","name: demo\ndependencies:\n  x: any\n")
        p, progress = self.plan()
        self.assertEqual(p["mode"],"full")
        self.assertTrue(p["pub_get"])
        self.write("test/a_test.dart","import 'helper.dart'; // updated\n")
        p, _ = self.plan(progress)
        self.assertEqual(p["tests"],["test/a_test.dart"])
        self.assertFalse(p["pub_get"])

    def test_conditional_and_part_and_comments(self):
        self.write("lib/part.dart","part of 'a.dart';\n")
        self.write("lib/a.dart","// import 'missing.dart';\npart 'part.dart';\n")
        self.write("lib/barrel.dart","export 'a.dart' if (dart.library.io) 'b.dart';\n")
        _, progress = self.plan()
        self.write("lib/part.dart","part of 'a.dart';\nint x=1;\n")
        p, _ = self.plan(progress)
        self.assertEqual(p["tests"],["test/a_test.dart"])
        self.assertEqual(scope.directives("@TestOn('vm') library;\nimport 'a.dart' if (dart.library.io == 'true') 'b.dart';\nvoid main() {}"),["a.dart","b.dart"])

    def test_unknown_asset_or_missing_import_falls_back(self):
        self.write("assets/catalog.json","{}")
        p, _ = self.plan()
        self.assertEqual(p["mode"],"full")
        self.assertIn("unclassified",p["reason"])
        (self.root/"assets/catalog.json").unlink()
        self.write("lib/a.dart","import 'missing.dart';")
        p, _ = self.plan()
        self.assertEqual(p["mode"],"full")
        self.assertIn("Unresolved",p["reason"])

    def test_uncovered_path_is_explicit(self):
        self.write("lib/uncovered.dart","int value=1;")
        p, _ = self.plan()
        self.assertEqual(p["mode"],"none")
        self.assertEqual(p["uncovered"],["lib/uncovered.dart"])
        self.assertTrue(p["analyze"])

    def test_environment_changes_invalidate_progress(self):
        self.write("lib/a.dart","int a=2;")
        _, progress = self.plan()
        self.write(".dart_tool/package_config.json",json.dumps({"packages":[{"name":"new"}]}))
        p, _ = self.plan(progress)
        self.assertEqual(p["mode"],"full")
        self.assertTrue(p["pub_get"])

    def test_reverted_change_is_not_silently_ignored(self):
        self.write("lib/a.dart","int a=2;")
        _, progress = self.plan()
        self.git("restore","lib/a.dart")
        p, _ = self.plan(progress)
        self.assertEqual(p["tests"],["test/a_test.dart"])
        self.assertEqual(p["changed"],["lib/a.dart"])


if __name__ == "__main__":
    unittest.main()

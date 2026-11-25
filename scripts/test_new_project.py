"""Preflight tests for an empty Git repository, without invoking Flutter."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("new_project", Path(__file__).with_name("new-project.py"))
new_project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(new_project)


class NewProjectPreflight(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "app"
        self.root.mkdir()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE)

    def init(self):
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Harness")
        self.git("config", "user.email", "test@example.invalid")
        self.git("remote", "add", "origin", "https://github.com/example/app.git")

    def check(self, name="vaqtpro", base="main"):
        return new_project.validate_target(self.root, name, base)

    def test_finder_metadata_with_git_history_and_remote(self):
        self.init()
        self.git("commit", "--allow-empty", "-m", "Empty repository")
        (self.root / ".DS_Store").write_bytes(b"metadata")
        before = self.git("rev-parse", "HEAD")
        self.assertTrue(self.check())
        self.assertEqual(self.git("rev-parse", "HEAD"), before)
        self.assertEqual(self.git("remote", "get-url", "origin").strip(), b"https://github.com/example/app.git")
        self.assertEqual((self.root / ".DS_Store").read_bytes(), b"metadata")

    def test_finder_metadata_without_git(self):
        (self.root / ".DS_Store").touch()
        self.assertFalse(self.check())

    def test_unborn_repository_with_metadata(self):
        self.init()
        (self.root / ".DS_Store").touch()
        self.assertTrue(self.check())

    def test_other_entries_are_named_and_preserved(self):
        self.init()
        (self.root / ".DS_Store").touch()
        (self.root / ".env.local").write_text("placeholder")
        (self.root / "README.md").touch()
        with self.assertRaisesRegex(ValueError, r"existing entries:.*\.env\.local.*README\.md"):
            self.check()
        self.assertTrue((self.root / ".env.local").exists())

    def test_invalid_name_and_wrong_branch_are_distinguished(self):
        self.init()
        with self.assertRaisesRegex(ValueError, "Invalid Flutter package name"):
            self.check("My-App")
        with self.assertRaisesRegex(ValueError, "Git branch is"):
            self.check(base="develop")

    def test_tracked_deletions_are_not_silently_committed(self):
        self.init()
        (self.root / "old.txt").touch()
        self.git("add", "old.txt")
        self.git("commit", "-m", "Old app")
        (self.root / "old.txt").unlink()
        with self.assertRaisesRegex(ValueError, "staged or unstaged changes"):
            self.check()
        self.git("add", "-u")
        self.git("commit", "-m", "Empty project")
        self.assertTrue(self.check())

    def test_metadata_directory_is_not_ignored(self):
        (self.root / ".DS_Store").mkdir()
        with self.assertRaisesRegex(ValueError, "existing entries"):
            self.check()


if __name__ == "__main__":
    unittest.main()

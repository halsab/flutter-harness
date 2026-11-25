"""Local deterministic tests, with real Git and mocked GitHub/Flutter."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

h = load("harness")
installer = load("install")


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "app"
        self.root.mkdir()
        self.remote = self.root.parent / "remote.git"
        self.git("init", "-b", "trunk")
        self.git("config", "user.name", "Harness")
        self.git("config", "user.email", "test@example.invalid")
        self.write("pubspec.yaml", "name: demo\n")
        self.write(".gitignore", "/.flutter-harness/work/\n/.flutter-harness/previews/\n")
        self.write("lib/main.dart", "old")
        self.c = {"schema": 2, "integration_branch": "trunk", "profile": "mobile-web"}
        self.write(".flutter-harness/config.json", json.dumps(self.c))
        self.write(".flutter-harness/product.json", "{}")
        self.git("add", ".")
        self.git("commit", "-m", "baseline")
        subprocess.run(["git","init","--bare",str(self.remote)],check=True,capture_output=True)
        self.git("remote","add","origin",str(self.remote))
        self.git("push","-u","origin","trunk")
        h.begin(self.root,self.c,"feature/test")

    def write(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(value, encoding="utf8")
        return p

    def git(self,*args):
        return subprocess.check_output(["git","-C",str(self.root),*args],stderr=subprocess.PIPE).decode().strip()

    def receipt(self, files):
        h.atomic_json(h.work(self.root)/"check.json", {"status":"PASS","digest":h.fingerprint(self.root)})
        h.atomic_json(h.work(self.root)/"delivery.json",{"files":files,"message":"feat: change","title":"Change","body":"Verified","required_e2e":[]})

    def test_candidate_covers_native_and_is_stable_across_commit(self):
        self.write("android/settings.gradle", "first")
        a = h.fingerprint(self.root)
        self.write("android/settings.gradle", "second")
        b = h.fingerprint(self.root)
        self.assertNotEqual(a,b)
        self.git("add",".")
        self.git("commit","-m","native")
        self.assertEqual(b,h.fingerprint(self.root))
        self.write(".flutter-harness/work/test.log","ignored")
        self.assertEqual(b,h.fingerprint(self.root))

    def test_missing_stale_or_unrelated_work_blocks_before_remote(self):
        self.write("lib/main.dart","new")
        self.receipt(["lib/main.dart"])
        self.write("lib/main.dart","changed")
        with self.assertRaisesRegex(h.Blocked,"stale"):
            h.deliver(self.root,self.c)
        self.write("notes.txt","unrelated")
        self.receipt(["lib/main.dart"])
        with self.assertRaisesRegex(h.Blocked,"Dirty files differ"):
            h.deliver(self.root,self.c)
        self.assertEqual(self.git("log","-1","--format=%s"),"baseline")

    def test_delivery_resumes_after_pr_create_failure_without_duplicate_commit(self):
        self.write("lib/main.dart","new")
        self.receipt(["lib/main.dart"])
        real = h.run
        state = {"exists":False,"create":0,"edit":0}
        def mocked(root,*args,**kwargs):
            if args[0] != "gh":
                return real(root,*args,**kwargs)
            cmd = args[2]
            if cmd == "list":
                items = [{"number":1,"baseRefName":"trunk","headRefName":"feature/test","isCrossRepository":False,"headRepositoryOwner":{"login":"owner"},"isDraft":False}] if state["exists"] else []
                return json.dumps(items).encode()
            if cmd == "create":
                state["create"] += 1
                if state["create"] == 1:
                    raise h.Blocked("temporary GitHub error")
                state["exists"] = True
                return b""
            if cmd == "edit":
                state["edit"] += 1
                return b""
            if cmd == "view":
                return json.dumps({"url":"https://github.com/owner/demo/pull/1","state":"OPEN","baseRefName":"trunk","headRefName":"feature/test","headRefOid":self.git("rev-parse","HEAD"),"isDraft":False,"isCrossRepository":False}).encode()
            raise AssertionError(args)
        with patch.object(h,"origin_repo",return_value="owner/demo"),patch.object(h,"run",side_effect=mocked):
            with self.assertRaisesRegex(h.Blocked,"temporary"):
                h.deliver(self.root,self.c)
            head = self.git("rev-parse","HEAD")
            h.deliver(self.root,self.c)
            h.deliver(self.root,self.c)
            self.assertEqual(self.git("rev-parse","HEAD"),head)
            self.assertEqual(self.git("rev-list","--count","trunk..HEAD"),"1")
            self.assertEqual(state["create"],2)
            self.assertEqual(state["edit"],1)

    def test_visual_requires_both_current_artifacts(self):
        digest = h.fingerprint(self.root)
        folder = self.root/".flutter-harness/previews"/digest
        folder.mkdir(parents=True)
        for theme in ("light","dark"):
            p = folder/(theme+".png")
            data = h.PNG+b"fixture content"
            p.write_bytes(data)
            h.atomic_json(p.with_suffix(".json"),{"digest":digest,"platform":"android","target":"emulator","theme":theme,"sha256":hashlib.sha256(data).hexdigest()})
        h.visual_evidence(self.root)
        (folder/"dark.png").write_bytes(b"changed")
        with self.assertRaises(h.Blocked):
            h.visual_evidence(self.root)
        self.write("lib/main.dart","another candidate")
        with self.assertRaises(h.Blocked):
            h.visual_evidence(self.root)


class InstallerTest(unittest.TestCase):
    def test_idempotent_preserves_user_text_and_conflict_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/"pubspec.yaml").write_text("name: demo\n")
            (root/"AGENTS.md").write_text("User policy.\n")
            installer.install(root,"mobile-web","trunk")
            cfg = root/".flutter-harness/config.json"
            first = cfg.read_bytes()
            installer.install(root,"mobile-web","trunk")
            self.assertEqual(first,cfg.read_bytes())
            self.assertIn("User policy.",(root/"AGENTS.md").read_text())
            self.assertIn('branches: ["trunk"]',(root/".github/workflows/flutter.yml").read_text())
            self.assertFalse((root/".opencode/skills/flutter-harness/SKILL.md").exists())
            script = root/".flutter-harness/bin/harness.py"
            script.write_text("local edit")
            with self.assertRaisesRegex(ValueError,"Local managed edits"):
                installer.install(root,"mobile","main")
            self.assertEqual(cfg.read_bytes(),first)
            self.assertEqual(script.read_text(),"local edit")

if __name__ == "__main__":
    unittest.main()

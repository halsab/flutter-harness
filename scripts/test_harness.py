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
        installer.install(self.root,"mobile-web","trunk")
        self.c = h.config(self.root)
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
        h.atomic_json(h.work(self.root)/"check.json", {"status":"PASS","digest":h.fingerprint(self.root),"checked_at":123})
        h.atomic_json(h.work(self.root)/"delivery.json",{"files":files,"message":"feat: change","title":"Change","body":"Verified","required_e2e":[]})

    def test_revision_mismatch_blocks_before_branch_switch(self):
        self.assertEqual(h.installed_revision(self.root,self.c)["revision"],self.c["revision"])
        with self.assertRaisesRegex(h.Blocked,"expected"):
            h.installed_revision(self.root,self.c,"0"*40)
        # A locally committed, internally consistent newer installation
        # must not be silently replaced by the fetched integration branch.
        cpath=self.root/".flutter-harness/config.json"
        mpath=self.root/".flutter-harness/managed.json"
        self.c["revision"]="1"*40
        cpath.write_text(json.dumps(self.c))
        m=h.read_json(mpath)
        m["revision"]=self.c["revision"]
        m["files"][".flutter-harness/config.json"]=hashlib.sha256(cpath.read_bytes()).hexdigest()
        h.atomic_json(mpath,m)
        self.git("add",".")
        self.git("commit","-m","sync pending")
        with self.assertRaisesRegex(h.Blocked,"different Harness revision"):
            h.begin(self.root,self.c,"feature/next")
        self.assertEqual(self.git("branch","--show-current"),"feature/test")

    def test_managed_file_tamper_rejected(self):
        self.write(".flutter-harness/PRODUCT.md","changed")
        with self.assertRaisesRegex(h.Blocked,"Managed Harness file differs"):
            h.installed_revision(self.root,self.c)

    def test_runtime_selection_stops_and_pins_successful_fallback(self):
        with patch.object(h,"runtime_targets",return_value=[("ios","phone"),("android","emu"),("web",None)]) as discovery, \
             patch.object(h,"probe_runtime",return_value=[390,844]) as probe, \
             patch.object(h,"launch",side_effect=[h.Blocked("launch failed"),{"status":"READY","platform":"android","target":"emu"}]) as launch:
            h.launch_auto(self.root,self.c)
            self.assertEqual(launch.call_count,2)
            self.assertEqual(probe.call_count,2)
            self.assertEqual(h.pinned_target(self.root),("android","emu"))
            launch.side_effect=None
            launch.return_value={"status":"READY","platform":"android","target":"emu"}
            h.launch_auto(self.root,self.c)
            self.assertEqual(discovery.call_count,1)
            self.assertEqual(launch.call_args.args[2:4],("android","emu"))
            launch.side_effect=h.Blocked("simulator stopped")
            with self.assertRaisesRegex(h.Blocked,"Pinned runtime failed"):
                h.launch_auto(self.root,self.c)
            self.assertEqual(h.pinned_target(self.root),("android","emu"))

    def test_preflight_stops_at_first_success(self):
        with patch.object(h,"runtime_targets",return_value=[("ios","phone"),("android","emu"),("web",None)]), \
             patch.object(h,"probe_runtime",return_value=[390,844]) as probe:
            h.visual_preflight(self.root,self.c)
            probe.assert_called_once_with(self.root,"ios","phone")
            self.assertEqual(h.read_json(h.work(self.root)/"visual-preflight.json")["ready"][0]["platform"],"ios")

    def test_device_preference_and_stable_phone_selection(self):
        devices=[{"id":"tablet","name":"iPad","targetPlatform":"ios","emulator":True},
                 {"id":"b","name":"iPhone Z","targetPlatform":"ios","emulator":True},
                 {"id":"a","name":"iPhone A","targetPlatform":"ios","emulator":True},
                 {"id":"real","name":"Phone","targetPlatform":"ios","emulator":False},
                 {"id":"emu","name":"Pixel","targetPlatform":"android-arm64","emulator":True}]
        with patch.object(h,"run",return_value=json.dumps(devices).encode()),patch.dict(os.environ,{"HARNESS_IOS_DEVICE":""}):
            self.assertEqual(h.runtime_targets(self.root,self.c),[("ios","a"),("android","emu"),("web",None)])
        with patch.object(h,"run",return_value=json.dumps(devices[::-1]).encode()),patch.dict(os.environ,{"HARNESS_IOS_DEVICE":"tablet"}):
            self.assertEqual(h.runtime_targets(self.root,self.c)[0],("ios","tablet"))

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
        state = {"exists":False,"create":0,"edit":0,"push":0,"body":"","title":"","head":""}
        def mocked(root,*args,**kwargs):
            if args[0] != "gh":
                if args[:2] == ("git", "push"):
                    state["push"] += 1
                return real(root,*args,**kwargs)
            cmd = args[2]
            if cmd == "list":
                items = [{"number":1,"baseRefName":"trunk","headRefName":"feature/test","isCrossRepository":False,"headRepositoryOwner":{"login":"owner"},"isDraft":False,"state":"OPEN","url":"https://github.com/owner/demo/pull/1","headRefOid":state["head"],"title":state["title"],"body":state["body"]}] if state["exists"] else []
                return json.dumps(items).encode()
            if cmd == "create":
                state["create"] += 1
                if state["create"] == 1:
                    raise h.Blocked("temporary GitHub error")
                state["exists"] = True
                state["head"] = self.git("rev-parse", "HEAD")
                state["title"] = args[args.index("--title")+1]
                state["body"] = Path(args[args.index("--body-file")+1]).read_text()
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
            result = h.completion(self.root,self.c)
            self.assertEqual(result["head"], head)
            (h.work(self.root)/"delivery-result.json").unlink()
            with self.assertRaisesRegex(h.Blocked, "Missing delivery-result"):
                h.completion(self.root,self.c)
            h.deliver(self.root,self.c)
            self.assertEqual(h.completion(self.root,self.c)["head"],head)
            self.assertEqual(self.git("rev-parse","HEAD"),head)
            self.assertEqual(self.git("rev-list","--count","trunk..HEAD"),"1")
            self.assertEqual(state["create"],2)
            self.assertEqual(state["edit"],0)
            self.assertEqual(state["push"],2)
            self.write("lib/main.dart", "newer")
            with self.assertRaisesRegex(h.Blocked, "Uncommitted"):
                h.completion(self.root,self.c)

    def visual_fixture(self):
        digest = h.fingerprint(self.root)
        folder = self.root/".flutter-harness/previews"/digest
        folder.mkdir(parents=True)
        plan = {"platform":"android","fixture":"mixed short/long realistic records","baseline":{"unavailable":"new screen"},
                "scenarios":[{"label":"final","kind":"screen"},{"label":"menu","kind":"interaction"}]}
        h.atomic_json(h.work(self.root)/"visual-plan.json", plan)
        h.atomic_json(h.work(self.root)/"visual-preflight.json", {"status":"PASS","branch":"feature/test","ready":[{"platform":"android","device":"emulator"}]})
        def write(label, theme, suffix):
            p = folder/(label+"-android-"+theme+".png")
            data = h.PNG+b"\x00\x00\x00\x0dIHDR"+h.struct.pack(">II",390,844)+b"\x08\x02\x00\x00\x00"+suffix
            p.write_bytes(data)
            h.atomic_json(p.with_suffix(".json"),{"digest":digest,"label":label,"platform":"android","target":"emulator",
                "theme":theme,"size":[390,844],"viewport":None,"sha256":hashlib.sha256(data).hexdigest()})
        return folder, write

    def test_visual_requires_current_complete_distinct_pairs(self):
        folder, write = self.visual_fixture()
        for theme in ("light","dark"):
            write("final", theme, theme.encode())
        with self.assertRaisesRegex(h.Blocked,"Missing capture receipt: menu"):
            h.visual_evidence(self.root, True)
        write("menu","light",b"same")
        write("menu","dark",b"same")
        with self.assertRaisesRegex(h.Blocked,"distinct"):
            h.visual_evidence(self.root, True)
        write("menu","dark",b"dark")
        first=h.visual_evidence(self.root, True)["evidence_digest"]
        preflight = h.work(self.root)/"visual-preflight.json"
        saved = preflight.read_bytes()
        preflight.unlink()
        with self.assertRaisesRegex(h.Blocked,"doctor visual"):
            h.visual_evidence(self.root, True)
        preflight.write_bytes(saved)
        write("menu","dark",b"new dark")
        self.assertNotEqual(first,h.visual_evidence(self.root, True)["evidence_digest"])
        (folder/"menu-android-dark.png").write_bytes(b"changed")
        with self.assertRaises(h.Blocked):
            h.visual_evidence(self.root, True)
        self.write("lib/main.dart","another candidate")
        with self.assertRaises(h.Blocked):
            h.visual_evidence(self.root, True)

    def test_runtime_lock_refuses_parallel_theme_changes(self):
        with h.target_lock("ios","test-device"):
            with self.assertRaisesRegex(h.Blocked,"busy"):
                with h.target_lock("ios","test-device"):
                    self.fail("concurrent capture")

    def test_web_launch_checks_chromium_before_build(self):
        with patch.object(h,"probe_runtime",side_effect=h.Blocked("no Chromium")), patch.object(h,"run",wraps=h.run) as runner:
            with self.assertRaisesRegex(h.Blocked,"no Chromium"):
                h.launch(self.root,self.c,"web",None)
            self.assertFalse(any("web-preview.py" in str(call) for call in runner.call_args_list))


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

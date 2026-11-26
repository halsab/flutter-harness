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

    def test_installed_cli_does_not_dirty_clean_project(self):
        import sys
        self.assertEqual(self.git("status", "--porcelain"), "")
        digest = h.fingerprint(self.root)
        cli = self.root / ".flutter-harness/bin/harness.py"
        for command in ("fingerprint", "status"):
            subprocess.run([sys.executable, str(cli), command], cwd=self.root,
                           check=True, capture_output=True)
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(h.fingerprint(self.root), digest)
        self.assertFalse((cli.parent / "__pycache__").exists())

    def test_begin_on_already_switched_new_branch_clears_previous_receipts(self):
        old = h.read_json(h.work(self.root)/"task.json")
        self.write(".flutter-harness/work/check.json", '{"status":"PASS"}')
        self.write(".flutter-harness/work/delivery-result.json", '{"status":"PASS"}')
        self.git("switch","-c","feature/next","origin/trunk")
        h.begin(self.root,self.c,"feature/next")
        current = h.read_json(h.work(self.root)/"task.json")
        self.assertEqual(current["branch"],"feature/next")
        self.assertGreaterEqual(current["started_at"],old["started_at"])
        self.assertFalse((h.work(self.root)/"check.json").exists())
        self.assertFalse((h.work(self.root)/"delivery-result.json").exists())
        h.begin(self.root,self.c,"feature/next")
        self.assertEqual(h.read_json(h.work(self.root)/"task.json"),current)

    def test_resume_existing_branch_after_integration_advanced_uses_fresh_evidence(self):
        old_base=self.git("rev-parse","origin/trunk")
        self.write("lib/main.dart","parked change")
        h.checkpoint_local(self.root,self.c,"feat: parked")
        parked=self.git("rev-parse","HEAD")
        self.write(".flutter-harness/work/check.json",'{"status":"PASS"}')
        self.git("switch","trunk")
        self.write("docs/new.md","integration advanced")
        self.git("add","docs/new.md")
        self.git("commit","-m","advance integration")
        self.git("push","origin","trunk")
        h.begin(self.root,self.c,"feature/test",resume=True)
        task=h.read_json(h.work(self.root)/"task.json")
        self.assertEqual(self.git("rev-parse","HEAD"),parked)
        self.assertEqual(task["base_head"],old_base)
        self.assertTrue(task["resumed"])
        self.assertFalse((h.work(self.root)/"check.json").exists())

    def test_diagnostics_uses_latest_task_in_same_session(self):
        for task in ("first","second"):
            h.event(self.root,"task-start",session="same",task=task)
            h.event(self.root,"task-complete",session="same",task=task)
        h.diagnostics(self.root,["same"],local_only=True)
        result=h.read_json(h.work(self.root)/"diagnostics.json")
        self.assertEqual([event.get("task") for event in result["events"]],["second","second"])

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

    def test_diagnostics_without_session_export(self):
        h.event(self.root,"task-start",session="ses_fixture")
        h.event(self.root,"check-run",artifacts=".flutter-harness/work/standard-fixture")
        self.write(".flutter-harness/work/standard-fixture/check-fixture.tsv","check\tstatus\texit_code\nflutter-tests\tTIMEOUT\t124\n")
        with patch.object(h,"usage",side_effect=h.Blocked("export unavailable")):
            h.diagnostics(self.root,[])
        data=h.read_json(h.work(self.root)/"diagnostics.json")
        self.assertEqual(data["usage_status"],"UNAVAILABLE")
        self.assertEqual(data["standard_runs"][0]["checks"][0]["status"],"TIMEOUT")
        self.assertFalse(data["check_running"])
        with patch.object(h,"usage") as exporter:
            h.diagnostics(self.root,["ses_fixture"],local_only=True)
            exporter.assert_not_called()
        self.assertEqual(h.read_json(h.work(self.root)/"diagnostics.json")["usage_status"],"NOT_REQUESTED")

    def test_check_cannot_run_concurrently(self):
        with (h.work(self.root)/"check.lock").open("a") as lock:
            h.fcntl.flock(lock,h.fcntl.LOCK_EX|h.fcntl.LOCK_NB)
            self.receipt(["lib/main.dart"])
            self.assertFalse(h.current_check(self.root,h.fingerprint(self.root)))
            with self.assertRaisesRegex(h.Blocked,"already running"):
                h.check(self.root,self.c)
        self.assertTrue(h.current_check(self.root,h.fingerprint(self.root)))

    def test_duplicate_begin_keeps_task_receipt(self):
        path = h.work(self.root)/"task.json"
        before = path.read_bytes()
        h.begin(self.root,self.c,"feature/test")
        self.assertEqual(path.read_bytes(),before)

    def test_changed_candidate_can_launch_without_intermediate_check(self):
        self.write("lib/main.dart","changed")
        with patch.object(h,"runtime_targets",return_value=[("ios","phone")]),patch.object(h,"probe_runtime",return_value=[390,844]),patch.object(h,"launch",return_value={"status":"READY","platform":"ios","target":"phone"}) as launch:
            h.launch_auto(self.root,self.c)
            launch.assert_called_once()

    def test_pinned_unchanged_runtime_reuses_prior_launch(self):
        h.atomic_json(h.work(self.root)/"runtime-selection.json",{"branch":"feature/test","platform":"ios","device":"phone"})
        h.atomic_json(h.work(self.root)/"runtime.json",{"platform":"ios","device":"phone","digest":h.fingerprint(self.root)})
        with patch.object(h,"probe_runtime",return_value=[390,844]),patch.object(h,"launch") as launch:
            h.launch_auto(self.root,self.c)
            launch.assert_not_called()
            launch.return_value={"status":"READY","platform":"ios","target":"phone"}
            h.launch_auto(self.root,self.c,fresh=True)
            launch.assert_called_once()

    def test_pinned_ios_runtime_reuses_android_and_test_helper_changes(self):
        h.atomic_json(h.work(self.root)/"runtime-selection.json",{"branch":"feature/test","platform":"ios","device":"phone"})
        old=h.fingerprint(self.root)
        scope=h.runtime_scope(self.root,"ios")
        h.atomic_json(h.work(self.root)/"runtime.json",{"platform":"ios","device":"phone","digest":old,"runtime_scope":scope})
        self.write("android/app/src/main/AndroidManifest.xml","other platform")
        self.write("test/helpers.dart","test helper")
        digest=h.fingerprint(self.root)
        self.assertNotEqual(old,digest)
        self.assertEqual(scope,h.runtime_scope(self.root,"ios"))
        h.atomic_json(h.work(self.root)/"check.json",{"status":"PASS","digest":digest})
        with patch.object(h,"probe_runtime",return_value=[390,844]),patch.object(h,"launch") as launch:
            h.launch_auto(self.root,self.c)
            launch.assert_not_called()
        self.write("maestro/flow.yaml","scenario only")
        self.assertEqual(scope,h.runtime_scope(self.root,"ios"))
        self.write("ios/Runner/Info.plist","affected platform")
        self.assertNotEqual(scope,h.runtime_scope(self.root,"ios"))

    def test_launch_does_not_capture_baseline_automatically(self):
        with patch.object(h,"runtime_targets",return_value=[("ios","phone")]),patch.object(h,"probe_runtime",return_value=[390,844]),patch.object(h,"launch",return_value={"status":"READY","platform":"ios","target":"phone"}),patch.object(h,"capture") as cap:
            h.launch_auto(self.root,self.c)
            cap.assert_not_called()

    def test_capture_reuse_requires_exact_image_and_scenario(self):
        p=self.write(".flutter-harness/work/capture.png","")
        data=h.PNG+b"\x00\x00\x00\x0dIHDR"+h.struct.pack(">II",390,844)+b"\x08\x02\x00\x00\x00"+b"crc!"
        p.write_bytes(data)
        expected={"scenario_sha256":"abc","digest":"candidate"}
        h.atomic_json(p.with_suffix(".json"),{**expected,"size":[390,844],"sha256":hashlib.sha256(data).hexdigest()})
        self.assertTrue(h.reusable_capture(p,expected))
        self.assertFalse(h.reusable_capture(p,{**expected,"scenario_sha256":"other"}))
        p.write_bytes(data+b"x")
        self.assertFalse(h.reusable_capture(p,expected))

    def test_capture_plan_runs_scripted_states_serially(self):
        self.write("maestro/screen.yaml","appId: dev.test\n---\n- launchApp\n")
        self.write("maestro/menu.yaml","appId: dev.test\n---\n- launchApp\n")
        digest = h.fingerprint(self.root)
        h.atomic_json(h.work(self.root)/"check.json",{"status":"PASS","digest":digest})
        h.atomic_json(h.work(self.root)/"runtime.json",{"platform":"ios","device":"phone","digest":digest})
        h.atomic_json(h.work(self.root)/"runtime-selection.json",{"branch":"feature/test","platform":"ios","device":"phone"})
        plan={"platform":"ios","fixture":"isolated test data","scenarios":[{"label":"main","kind":"screen","scenario":"maestro/screen.yaml","themes":["light","dark"]},
                {"label":"menu","kind":"interaction","scenario":"maestro/menu.yaml","themes":["light","dark"]}]}
        h.atomic_json(h.work(self.root)/"visual-plan.json",plan)
        with patch.object(h,"capture") as cap,patch.object(h,"visual_evidence") as evidence:
            h.capture_plan(self.root,self.c)
            self.assertEqual([(x.args[2],x.args[3],x.kwargs["scenario"]) for x in cap.call_args_list],
                 [("main","light","maestro/screen.yaml"),("main","dark","maestro/screen.yaml"),
                  ("menu","light","maestro/menu.yaml"),("menu","dark","maestro/menu.yaml")])
            evidence.assert_called_once_with(self.root,True)
            cap.reset_mock()
            plan["scenarios"][1].pop("scenario")
            h.atomic_json(h.work(self.root)/"visual-plan.json",plan)
            with self.assertRaisesRegex(h.Blocked,"scripted scenario"):
                h.capture_plan(self.root,self.c)
            cap.assert_not_called()

    def test_prepare_delivery_defaults_and_early_validation(self):
        self.write("lib/main.dart","new")
        a = h.argparse.Namespace(message="change",title="Change",body="description",review=False,visual=False,interaction=True,e2e=[])
        h.prepare_delivery(self.root,self.c,a)
        m=h.delivery_manifest(self.root,self.c)
        self.assertEqual(m["files"],["lib/main.dart"])
        self.assertEqual(m["required_e2e"],[])
        self.assertTrue(m["visual_required"])
        self.assertTrue(m["visual_interaction"])
        m["required_e2e"]="none"
        h.atomic_json(h.work(self.root)/"delivery.json",m)
        with self.assertRaisesRegex(h.Blocked,"Invalid required_e2e"):
            h.delivery_manifest(self.root,self.c)

    def test_explicit_verification_plan_correction_before_publication(self):
        self.write("lib/main.dart","new")
        a=h.argparse.Namespace(message="change",title="Change",body="Verified",review=False,visual=True,interaction=False,e2e=[])
        h.prepare_delivery(self.root,self.c,a)
        a.visual=False
        h.prepare_delivery(self.root,self.c,a)
        self.assertTrue(h.delivery_manifest(self.root,self.c)["visual_required"])
        a.revise_verification="Only a statically verifiable style correction"
        h.prepare_delivery(self.root,self.c,a)
        manifest=h.delivery_manifest(self.root,self.c)
        self.assertFalse(manifest["visual_required"])
        self.assertEqual(manifest["verification_revision_reason"],a.revise_verification)

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

    def test_required_platform_never_falls_back(self):
        with patch.object(h,"runtime_targets",return_value=[("android","emu")]) as discovery, \
             patch.object(h,"probe_runtime",side_effect=h.Blocked("Android unavailable")):
            with self.assertRaisesRegex(h.Blocked,"No runtime target"):
                h.launch_auto(self.root,self.c,"android")
            discovery.assert_called_once_with(self.root,self.c,"android")
            self.assertIsNone(h.pinned_target(self.root))

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
        state = {"exists":False,"create":0,"edit":0,"push":0,"body":"","title":"","head":"","url":"https://github.com/owner/demo/pull/1","timeout_after_create":False}
        def mocked(root,*args,**kwargs):
            if args[0] != "gh":
                if args[:2] == ("git", "push"):
                    state["push"] += 1
                return real(root,*args,**kwargs)
            cmd = args[2]
            if args[:3] == ("gh", "repo", "view"):
                self.assertEqual(args[3], "owner/old-demo")
                return json.dumps({"nameWithOwner":"owner/demo","id":"R_demo"}).encode()
            if cmd == "list":
                self.assertEqual(args[args.index("--repo")+1],"owner/demo")
                items = [{"number":1,"baseRefName":"trunk","headRefName":"feature/test","isCrossRepository":False,"headRepositoryOwner":{"login":"owner"},"isDraft":False,"state":"OPEN","url":state["url"],"headRefOid":state["head"],"title":state["title"],"body":state["body"]}] if state["exists"] else []
                return json.dumps(items).encode()
            if cmd == "create":
                state["create"] += 1
                if state["create"] == 1:
                    raise h.Blocked("temporary GitHub error")
                state["exists"] = True
                state["head"] = self.git("rev-parse", "HEAD")
                state["title"] = args[args.index("--title")+1]
                state["body"] = Path(args[args.index("--body-file")+1]).read_text()
                if state["timeout_after_create"]:
                    raise subprocess.TimeoutExpired(args, 60)
                return b""
            if cmd == "edit":
                state["edit"] += 1
                return b""
            if cmd == "view":
                return json.dumps({"url":"https://github.com/owner/demo/pull/1","state":"OPEN","baseRefName":"trunk","headRefName":"feature/test","headRefOid":self.git("rev-parse","HEAD"),"isDraft":False,"isCrossRepository":False}).encode()
            raise AssertionError(args)
        with patch.object(h,"origin_repo",return_value="owner/old-demo"),patch.object(h,"run",side_effect=mocked):
            with self.assertRaisesRegex(h.Blocked,"temporarily"):
                h.deliver(self.root,self.c)
            head = self.git("rev-parse","HEAD")
            failure = h.read_json(h.work(self.root)/"delivery-state.json")
            self.assertEqual(failure["stage"], "delivery-pushed")
            self.assertEqual(failure["error"]["code"], "PR_CREATE_TRANSIENT")
            self.assertTrue(failure["error"]["retryable"])
            with self.assertRaises(h.DeliveryBlocked) as error:
                h.completion(self.root,self.c)
            self.assertEqual(error.exception.code, "PR_CREATE_TRANSIENT")
            # The CLI exposes the structured cause to OpenCode without network calls.
            import sys
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch.object(sys,"argv",["harness.py","--project",str(self.root),"completion"]), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(h.main(),3)
            self.assertEqual(json.loads(stdout.getvalue())["error"]["code"],"PR_CREATE_TRANSIENT")
            self.assertIn("PR_CREATE temporarily unavailable",stderr.getvalue())
            # A different manifest must not inherit a previous attempt's failure.
            manifest_path = h.work(self.root)/"delivery.json"
            manifest = h.read_json(manifest_path)
            h.atomic_json(manifest_path,{**manifest,"title":"Changed"})
            with self.assertRaisesRegex(h.Blocked,"Missing delivery-result"):
                h.completion(self.root,self.c)
            h.atomic_json(manifest_path,manifest)
            h.deliver(self.root,self.c)
            with patch.object(h,"canonical_repo",side_effect=AssertionError("completion must stay offline")):
                result = h.completion(self.root,self.c)
            self.assertEqual(result["head"], head)
            self.assertEqual(result["repo"], "owner/demo")
            self.assertEqual(result["origin_repo"], "owner/old-demo")
            self.assertEqual(result["repo_id"], "R_demo")
            self.assertEqual(result["pr_number"], 1)
            self.assertEqual(h.verify(self.root,self.c)["number"], 1)
            with patch.object(h,"canonical_repo",return_value=("owner/demo","R_other")):
                with self.assertRaisesRegex(h.Blocked,"Remote repository differs"):
                    h.verify(self.root,self.c)
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
            # Existing remote PR, but receipt lost and remote identity inconsistent.
            (h.work(self.root)/"delivery-result.json").unlink()
            state["url"] = "https://github.com/owner/other/pull/1"
            with self.assertRaisesRegex(h.Blocked,"Unexpected PR URL"):
                h.deliver(self.root,self.c)
            with self.assertRaises(h.DeliveryBlocked) as error:
                h.completion(self.root,self.c)
            self.assertEqual(error.exception.code,"PR_URL_MISMATCH")
            self.assertFalse(error.exception.retryable)
            self.assertEqual(state["create"],2)
            self.assertEqual(state["push"],2)
            state["url"] = "https://github.com/owner/demo/pull/1"
            h.deliver(self.root,self.c)
            self.assertEqual(h.completion(self.root,self.c)["head"],head)
            # Simulate an ambiguous create: GitHub created the PR, but the CLI timed out.
            (h.work(self.root)/"delivery-result.json").unlink()
            state["exists"] = False
            state["timeout_after_create"] = True
            with self.assertRaises(h.DeliveryBlocked) as error:
                h.deliver(self.root,self.c)
            self.assertEqual(error.exception.code,"PR_CREATE_TIMEOUT")
            self.assertTrue(error.exception.retryable)
            self.assertTrue(state["exists"])
            self.assertEqual(state["create"],3)
            self.assertEqual(state["push"],3)
            h.deliver(self.root,self.c)
            self.assertEqual(state["create"],3)
            self.assertEqual(state["push"],3)
            self.assertEqual(h.completion(self.root,self.c)["head"],head)
            self.write("lib/main.dart", "newer")
            with self.assertRaisesRegex(h.Blocked, "Uncommitted"):
                h.completion(self.root,self.c)

    def test_origin_formats_and_canonical_resolution(self):
        for url in ("https://github.com/owner/old-demo.git", "git@github.com:owner/old-demo.git",
                    "ssh://git@github.com/owner/old-demo"):
            with self.subTest(url=url), patch.object(h,"git",return_value=url.encode()):
                self.assertEqual(h.origin_repo(self.root),"owner/old-demo")
        with patch.object(h,"git",side_effect=[b"https://github.com/owner/demo.git", b"https://github.com/owner/other.git"]):
            with self.assertRaisesRegex(h.Blocked,"Push URL differs"):
                h.origin_repo(self.root)

    def test_strict_pr_identity_and_remote_classification(self):
        pr = {"number":1,"url":"https://github.com/owner/demo/pull/1","state":"OPEN",
              "baseRefName":"trunk","headRefName":"feature/test","headRefOid":"abc",
              "isCrossRepository":False,"isDraft":False}
        self.assertEqual(h.validate_remote_pr(pr,"owner/demo","trunk","feature/test","abc"),pr)
        for change in ({"url":pr["url"]+"/files"}, {"number":2}, {"url":"https://github.com/owner/other/pull/1"},
                       {"baseRefName":"wrong"}, {"headRefOid":"stale"}, {"isCrossRepository":True},
                       {"isDraft":True}, {"state":"CLOSED"}):
            with self.subTest(change=change), self.assertRaises(h.DeliveryBlocked):
                h.validate_remote_pr({**pr,**change},"owner/demo","trunk","feature/test","abc")
        for message, code, retryable in (("HTTP 503", "PR_LIST_TRANSIENT", True),
                                        ("HTTP 403 Forbidden", "PR_LIST_ACCESS", False),
                                        ("unexpected output", "PR_LIST_FAILED", False)):
            with patch.object(h,"run",side_effect=h.Blocked(message)):
                with self.assertRaises(h.DeliveryBlocked) as error:
                    h.remote_call("PR_LIST", h.run, self.root)
                self.assertEqual(error.exception.code,code)
                self.assertEqual(error.exception.retryable,retryable)

    def visual_fixture(self):
        digest = h.fingerprint(self.root)
        self.write("maestro/menu.yaml","appId: dev.test\n---\n- launchApp\n- tapOn: Menu\n")
        digest = h.fingerprint(self.root)
        folder = h.visual_folder(self.root,"android",digest)
        folder.mkdir(parents=True)
        scope = h.visual_scope(self.root,"android")
        plan = {"platform":"android","fixture":"mixed short/long realistic records","scenarios":[{"label":"final","kind":"screen","themes":["light","dark"]},{"label":"menu","kind":"interaction","scenario":"maestro/menu.yaml","themes":["light","dark"]}]}
        h.atomic_json(h.work(self.root)/"visual-plan.json", plan)
        h.atomic_json(h.work(self.root)/"visual-preflight.json", {"status":"PASS","branch":"feature/test","ready":[{"platform":"android","device":"emulator"}]})
        def write(label, theme, suffix):
            p = folder/(label+"-android-"+theme+".png")
            data = h.PNG+b"\x00\x00\x00\x0dIHDR"+h.struct.pack(">II",390,844)+b"\x08\x02\x00\x00\x00"+suffix
            p.write_bytes(data)
            h.atomic_json(p.with_suffix(".json"),{"digest":digest,"visual_scope":scope,"label":label,"platform":"android","target":"emulator",
                "theme":theme,"size":[390,844],"viewport":None,"fixture":plan["fixture"],
                "scenario":"maestro/menu.yaml" if label=="menu" else None,
                "scenario_sha256":hashlib.sha256((self.root/"maestro/menu.yaml").read_bytes()).hexdigest() if label=="menu" else None,
                "sha256":hashlib.sha256(data).hexdigest()})
        return folder, write

    def test_single_theme_final_screen_without_script(self):
        self.write("lib/main.dart","new candidate")
        _,write=self.visual_fixture()
        path=h.work(self.root)/"visual-plan.json"
        plan=h.read_json(path)
        plan["scenarios"]=[{"label":"final","kind":"screen"}]
        h.atomic_json(path,plan)
        write("final","light",b"light")
        result=h.visual_evidence(self.root)
        self.assertEqual(len(result["captures"]),1)
        self.assertEqual(result["captures"][0]["theme"],"light")

    def test_visual_accepts_no_baseline(self):
        self.write("lib/main.dart","new candidate")
        _,write=self.visual_fixture()
        for label in ("final","menu"):
            for theme in ("light","dark"):
                write(label,theme,theme.encode())
        result=h.visual_evidence(self.root,True)
        self.assertEqual(result["status"],"PASS")
        self.assertIsNone(result["baseline"])

    def test_visual_reuses_other_platform_and_test_only_changes(self):
        self.write("lib/main.dart","new candidate")
        _,write=self.visual_fixture()
        for label in ("final","menu"):
            for theme in ("light","dark"):
                write(label,theme,theme.encode())
        before=h.visual_evidence(self.root,True)
        self.write("ios/Runner/Info.plist","other platform")
        self.write("test/persistence_test.dart","new test")
        self.write("test/fixtures/helper.dart","changed test helper")
        after=h.visual_evidence(self.root,True)
        self.assertNotEqual(before["digest"],after["digest"])
        self.assertEqual(before["evidence_digest"],after["evidence_digest"])
        self.write("android/app/src/main/AndroidManifest.xml","affected platform")
        with self.assertRaises(h.Blocked):
            h.visual_evidence(self.root,True)

    def test_visual_scope_keeps_shared_config_assets_and_scripts(self):
        self.write("lib/main.dart","new candidate")
        _,write=self.visual_fixture()
        for label in ("final","menu"):
            for theme in ("light","dark"):
                write(label,theme,theme.encode())
        before=h.visual_scope(self.root,"android")
        self.write("maestro/menu.yaml","different flow")
        self.assertNotEqual(before,h.visual_scope(self.root,"android"))
        before=h.visual_scope(self.root,"android")
        self.write("assets/catalog.json","new content")
        self.assertNotEqual(before,h.visual_scope(self.root,"android"))

    def test_local_checkpoint_preserves_full_candidate_and_can_prepare_clean_delivery(self):
        self.write("lib/main.dart","slice one")
        before=h.fingerprint(self.root)
        h.checkpoint_local(self.root,self.c,"feat: first slice")
        self.assertEqual(self.git("status","--porcelain"),"")
        self.assertEqual(before,h.fingerprint(self.root))
        self.write("lib/second.dart","slice two")
        h.checkpoint_local(self.root,self.c,"feat: second slice")
        self.assertEqual(self.git("rev-list","--count","origin/trunk..HEAD"),"2")
        a=h.argparse.Namespace(message="change",title="Change",body="Verified",review=True,visual=False,interaction=False,e2e=[])
        h.prepare_delivery(self.root,self.c,a)
        self.assertEqual(h.delivery_manifest(self.root,self.c)["files"],[])
        self.assertTrue(h.delivery_manifest(self.root,self.c)["review_required"])

    def test_draft_backup_requires_clean_checkpoint_and_never_delivers(self):
        self.write("lib/main.dart","work in progress")
        with self.assertRaisesRegex(h.Blocked,"checkpoint first"):
            h.save_draft(self.root,self.c)
        h.checkpoint_local(self.root,self.c,"feat: save")
        head=self.git("rev-parse","HEAD")
        pr={"state":"OPEN","baseRefName":"trunk","headRefName":"feature/test",
            "headRefOid":head,"isCrossRepository":False,"isDraft":True,"number":12,
            "url":"https://github.com/owner/repo/pull/12"}
        with patch.object(h,"origin_repo",return_value="owner/repo"),patch.object(h,"canonical_repo",return_value=("owner/repo","1")),patch.object(h,"pr_list",side_effect=[None,pr]),patch.object(h,"remote_call",side_effect=lambda op,fn,*args,**kwargs: fn(*args,**kwargs) if op=="PR_LIST" else None) as remote:
            h.save_draft(self.root,self.c)
            self.assertIn("--draft",next(c.args for c in remote.call_args_list if c.args[0]=="PR_CREATE"))
        self.assertEqual(h.draft_completion(self.root,self.c)["status"],"DRAFT_SAVED")
        self.assertFalse((h.work(self.root)/"delivery-result.json").exists())
        with patch.object(h,"origin_repo",return_value="owner/repo"),patch.object(h,"canonical_repo",return_value=("owner/repo","1")),patch.object(h,"pr_list",return_value={**pr,"isDraft":False}):
            with self.assertRaisesRegex(h.Blocked,"ready"):
                h.save_draft(self.root,self.c)

    def test_large_uncommitted_slice_does_not_force_checkpoint_before_runtime(self):
        self.write("lib/large.dart","// generated\n"*401)
        with patch.object(h,"runtime_targets",return_value=[("ios","phone")]),patch.object(h,"probe_runtime",return_value=[390,844]),patch.object(h,"launch",return_value={"status":"READY","platform":"ios","target":"phone"}) as launch:
            h.launch_auto(self.root,self.c)
            launch.assert_called_once()
        self.assertTrue(h.dirty(self.root))

    def test_checkpoint_can_save_work_after_blocked_delivery(self):
        self.write("lib/main.dart","new candidate")
        h.atomic_json(h.work(self.root)/"delivery-state.json",{"status":"BLOCKED","digest":"old"})
        h.checkpoint_local(self.root,self.c,"fix: preserve")
        self.assertFalse(h.dirty(self.root))

    def test_failed_scope_keeps_last_success_and_retry_selects_changed_test(self):
        self.write(".gitignore","/.flutter-harness/work/\n/.flutter-harness/previews/\n/.dart_tool/\n")
        # Save ignore config in the first verified candidate, then make test-only edits.
        self.write(".dart_tool/package_config.json",'{"packages":[]}')
        self.write("lib/main.dart","int x=1;")
        self.write("test/a_test.dart","import '../lib/main.dart';\n")
        self.write("test/b_test.dart","void main() {}\n")
        real=h.run
        fail=False
        invocations=[]
        def fake(root,*args,**kw):
            nonlocal fail
            if args[0] in ("flutter","dart"):
                invocations.append(args)
                return b""
            if args[0]=="bash" and str(args[1]).endswith("check.sh"):
                plan=h.read_json(h.Path(args[-1]))
                invocations.append(("runner",plan))
                folder=h.Path(kw["env"]["HARNESS_ARTIFACTS_DIR"])
                flags={"format":bool(plan["format"]),"product":plan["product"],
                       "analyze":plan["analyze"],"flutter-tests":plan["mode"]!="none"}
                rows=["check\tstatus\texit_code"]
                for label,enabled in flags.items():
                    status="FAIL" if fail and label=="flutter-tests" else "PASS" if enabled else "SKIP"
                    rows.append(f"{label}\t{status}\t{1 if status=='FAIL' else 0}")
                (folder/"check-fake.tsv").write_text("\n".join(rows)+"\n")
                if fail:
                    raise h.Blocked("test failure")
                return b""
            return real(root,*args,**kw)
        with patch.object(h,"run",side_effect=fake):
            h.check(self.root,self.c)
            prior=(h.work(self.root)/"check-progress.json").read_bytes()
            self.write("test/a_test.dart","import '../lib/main.dart'; // regression\n")
            fail=True
            with self.assertRaisesRegex(h.Blocked,"test failure"):
                h.check(self.root,self.c)
            self.assertEqual((h.work(self.root)/"check-progress.json").read_bytes(),prior)
            self.assertFalse(h.current_check(self.root,h.fingerprint(self.root)))
            self.write("test/a_test.dart","import '../lib/main.dart'; // repaired\n")
            fail=False
            h.check(self.root,self.c)
            self.assertEqual(invocations[-1][1]["tests"],["test/a_test.dart"])
            self.assertFalse(invocations[-1][1]["pub_get"])
            self.assertTrue(h.current_check(self.root,h.fingerprint(self.root)))
            count=len(invocations)
            h.check(self.root,self.c)
            self.assertEqual(len(invocations),count)

    def test_repeated_unchanged_failed_check_stops_without_another_runner(self):
        self.write("lib/main.dart","changed")
        with patch.object(h,"check_candidate",side_effect=h.Blocked("test failure")) as runner:
            for _ in range(2):
                with self.assertRaisesRegex(h.Blocked,"test failure"):
                    h.check(self.root,self.c)
            with self.assertRaisesRegex(h.Blocked,"failed twice"):
                h.check(self.root,self.c)
            self.assertEqual(runner.call_count,2)
            self.write("lib/main.dart","fixed")
            with self.assertRaisesRegex(h.Blocked,"test failure"):
                h.check(self.root,self.c)
            self.assertEqual(runner.call_count,3)

    def test_identical_successful_check_reused(self):
        self.write("lib/main.dart","verified")
        self.receipt(["lib/main.dart"])
        with patch.object(h,"check_candidate") as check:
            h.check(self.root,self.c)
            check.assert_not_called()
        self.write("lib/main.dart","different")
        with patch.object(h,"check_candidate") as check:
            h.check(self.root,self.c)
            check.assert_called_once()

    def test_visual_rejects_unrelated_baseline(self):
        self.write("lib/main.dart","new candidate")
        folder,write=self.visual_fixture()
        for label in ("final","menu"):
            for theme in ("light","dark"):
                write(label,theme,theme.encode())
        path=h.work(self.root)/"visual-plan.json"
        plan=h.read_json(path)
        plan["baseline"]={"digest":"a"*64,"label":"baseline"}
        h.atomic_json(path,plan)
        with self.assertRaisesRegex(h.Blocked,"original candidate"):
            h.visual_evidence(self.root,True)

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

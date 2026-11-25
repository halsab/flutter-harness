"""Real local Git worktrees; mocked device discovery and remote PR metadata."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import harness as h
import workspace as w
import install

class Workspaces(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)/"app"
        self.root.mkdir()
        self.remote=Path(tmp.name)/"remote.git"
        self.git(self.root,"init","-b","app")
        self.git(self.root,"config","user.name","Harness")
        self.git(self.root,"config","user.email","test@example.invalid")
        (self.root/"pubspec.yaml").write_text("name: example\n")
        (self.root/"lib.txt").write_text("base\n")
        install.install(self.root,"mobile-web","app")
        self.c=h.config(self.root)
        self.git(self.root,"add",".")
        self.git(self.root,"commit","-m","base")
        subprocess.run(["git","init","--bare",str(self.remote)],check=True,capture_output=True)
        self.git(self.root,"remote","add","origin",str(self.remote))
        self.git(self.root,"push","-u","origin","app")
        slotdir=Path(tmp.name)/"slots"
        patcher=patch.object(h,"slot_path",side_effect=lambda platform:slotdir/(platform+".json"))
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher=patch.object(h,"runtime_targets",side_effect=lambda root,c,only=None:[
            x for x in [("ios","phone"),("android","emulator"),("web",None)] if only in (None,x[0])])
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher=patch.object(h,"probe_runtime",return_value=[390,844])
        patcher.start()
        self.addCleanup(patcher.stop)

    def git(self,root,*args):
        return subprocess.check_output(["git","-C",str(root),*args],stderr=subprocess.PIPE,text=True).strip()

    def make(self,name,only=None):
        lease=w.create(self.root,self.c,name,only)
        path=Path(lease["root"])
        return path,lease

    def commit(self,path,file,content):
        (path/file).write_text(content)
        self.git(path,"add",file)
        self.git(path,"commit","-m","change "+file)
        return self.git(path,"rev-parse","HEAD")

    def test_three_slots_isolation_and_assigned_branch(self):
        a,la=self.make("one")
        b,lb=self.make("two")
        c,lc=self.make("three")
        self.assertEqual([la["platform"],lb["platform"],lc["platform"]],["ios","android","web"])
        self.assertEqual(self.git(self.root,"branch","--show-current"),"app")
        self.assertEqual(w.common(a),w.common(b))
        self.assertEqual(h.workspace_assignment(a),la)
        self.assertEqual(h.workspace_assignment(b),lb)
        self.assertEqual(h.workspace_assignment(c),lc)
        with self.assertRaisesRegex(h.Blocked,"Three workspaces"):
            self.make("four")
        self.commit(a,"lib.txt","one\n")
        self.assertEqual((b/"lib.txt").read_text(),"base\n")
        self.assertEqual((self.root/"lib.txt").read_text(),"base\n")
        with h.runtime_access(a,"ios","phone"):
            pass
        with self.assertRaisesRegex(h.Blocked,"not reserved"):
            with h.runtime_access(b,"ios","phone"):
                self.fail("foreign device")
        with self.assertRaisesRegex(h.Blocked,"reserved by another"):
            with h.runtime_access(self.root,"ios","phone"):
                self.fail("legacy device overwrite")
        with self.assertRaisesRegex(h.Blocked,"preassigned"):
            h.begin(b,h.config(b),"wrong-branch")
        h.begin(b,h.config(b),"two")
        self.assertEqual(h.read_json(h.work(b)/"task.json")["branch"],"two")
        with self.assertRaisesRegex(h.Blocked,"Device differs"):
            h.assert_runtime_access(a,"ios","another-phone")

    def test_platform_specific_no_fallback(self):
        self.make("native","ios")
        with self.assertRaisesRegex(h.Blocked,"occupied"):
            self.make("second","ios")
        self.assertEqual(len(w.entries(self.root)),1)

    def test_wrapper_lock_and_cwd(self):
        path,lease=self.make("task")
        with patch.object(w.subprocess,"call",return_value=0) as run:
            self.assertEqual(w.start(self.root,"task"),0)
            self.assertEqual(run.call_args.kwargs["cwd"],path)
            self.assertEqual(run.call_args.kwargs["env"]["HARNESS_WORKSPACE_ROOT"],str(path))
            with w.lock(w.session_lock(self.root,"task")):
                with self.assertRaisesRegex(h.Blocked,"already active"):
                    w.start(self.root,"task")

    def setup_batch(self,conflict=False):
        paths=[self.make(n)[0] for n in ("one","two","three")]
        items=[]
        for i,path in enumerate(paths,1):
            file="lib.txt" if conflict and i<=2 else "task"+str(i)+".txt"
            head=self.commit(path,file,str(i)+"\n")
            items.append({"branch":path.name,"head":head,"number":i,"url":"https://github.com/owner/demo/pull/"+str(i)})
        return paths,items

    def check_batch(self,items,fail_at=None):
        real_run=subprocess.run
        checks=[]
        def run(args,**kwargs):
            if args[-1:]==["ci"] and "harness.py" in str(args):
                checks.append(sorted(p.name for p in kwargs["cwd"].glob("task*.txt")))
                return subprocess.CompletedProcess(args,1 if len(checks)==fail_at else 0)
            return real_run(args,**kwargs)
        with patch.object(h,"origin_repo",return_value="owner/demo"),patch.object(w,"delivered",side_effect=lambda root,n,repo,base:next(x for x in items if x["branch"]==n)),patch.object(w,"verify_pr"),patch.object(w.subprocess,"run",side_effect=run):
            result=w.integration_check(self.root,self.c,[x["branch"] for x in items])
        return result,checks

    def test_cumulative_prefixes_and_next_order(self):
        paths,items=self.setup_batch()
        report,checks=self.check_batch(items)
        self.assertEqual(report["status"],"PASS")
        self.assertEqual(checks,[["task1.txt"],["task1.txt","task2.txt"],["task1.txt","task2.txt","task3.txt"]])
        self.assertFalse((self.root/"task1.txt").exists())
        self.assertFalse((paths[0]/"task2.txt").exists())
        states={x["number"]:"OPEN" for x in items}
        def state(root,repo,n):
            item=items[n-1]
            return {"state":states[n],"headRefOid":item["head"],"headRefName":item["branch"],"baseRefName":"app","isCrossRepository":False,"isDraft":False}
        with patch.object(h,"origin_repo",return_value="owner/demo"),patch.object(w,"pr_state",side_effect=state):
            self.assertEqual(w.next_pr(self.root,self.c)["number"],1)
            self.git(self.root,"merge","--squash",items[0]["head"])
            self.git(self.root,"commit","-m","owner merge 1")
            self.git(self.root,"push","origin","app")
            states[1]="MERGED"
            self.assertEqual(w.next_pr(self.root,self.c)["number"],2)
            states[3]="MERGED"
            with self.assertRaisesRegex(h.Blocked,"PR state/head changed"):
                w.next_pr(self.root,self.c)
            states[3]="OPEN"
            self.commit(self.root,"other.txt","unexpected")
            self.git(self.root,"push","origin","app")
            with self.assertRaisesRegex(h.Blocked,"Base tree differs"):
                w.next_pr(self.root,self.c)

    def test_conflict_and_combined_failure_block_batch(self):
        _,items=self.setup_batch(conflict=True)
        with self.assertRaisesRegex(h.Blocked,"Integration conflict at two"):
            self.check_batch(items)
        report=h.read_json(w.registry(self.root)/"integration.json")
        self.assertEqual(report["status"],"BLOCKED")
        self.assertEqual(report["checked"],1)
        self.assertTrue(Path(report["logs"]).is_dir())

    def test_failed_combined_test_is_not_ready(self):
        _,items=self.setup_batch()
        with self.assertRaisesRegex(h.Blocked,"Combined verification failed at two"):
            self.check_batch(items,fail_at=2)
        self.assertEqual(h.read_json(w.registry(self.root)/"integration.json")["status"],"BLOCKED")

    def test_cleanup_preserves_dirty_or_unmerged(self):
        path,lease=self.make("task")
        (path/"unfinished.txt").write_text("preserve")
        with self.assertRaisesRegex(h.Blocked,"uncommitted"):
            w.clean(self.root,self.c,"task")
        self.assertTrue((path/"unfinished.txt").is_file())
        (path/"unfinished.txt").unlink()
        head=self.git(path,"rev-parse","HEAD")
        result={"head":head,"pr":"https://github.com/owner/demo/pull/1"}
        with patch.object(h,"origin_repo",return_value="owner/demo"),patch.object(h,"completion",return_value=result),patch.object(w,"verify_pr",side_effect=h.Blocked("not merged")):
            with self.assertRaisesRegex(h.Blocked,"not merged"):
                w.clean(self.root,self.c,"task")
        self.assertTrue(path.is_dir())
        self.assertEqual(h.slot_owner("ios"),lease)
        with patch.object(h,"origin_repo",return_value="owner/demo"),patch.object(h,"completion",return_value=result),patch.object(w,"verify_pr"):
            w.clean(self.root,self.c,"task")
        self.assertFalse(path.exists())
        self.assertIsNone(h.slot_owner("ios"))
        self.assertEqual(w.entries(self.root),{})

if __name__=="__main__":
    unittest.main()

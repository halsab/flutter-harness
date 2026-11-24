import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "task_plan", Path(__file__).with_name("task-plan.py"))
plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan)


def task(key, *, deps=(), reads=(), writes=(), status="pending"):
    item = dict(id=key, goal=key, depends_on=list(deps), reads=list(reads),
                writes=list(writes), acceptance=["observable outcome"], status=status)
    if status == "done":
        item["evidence"] = "targeted assertion passed"
    return item


def graph(*tasks):
    return dict(schema=1, goal="feature", tasks=list(tasks))


class TaskPlanTests(unittest.TestCase):
    def test_independent_wave_then_integration(self):
        a = task("a", writes=["lib/a.dart"])
        b = task("b", writes=["lib/b.dart"])
        c = task("c", deps=["a", "b"], reads=["lib/a.dart", "lib/b.dart"])
        p = graph(a, b, c)
        self.assertEqual(plan.ready(p), ["a", "b"])
        a["status"] = b["status"] = "running"
        self.assertEqual(plan.ready(p), [])
        a.update(status="done", evidence="unit passed")
        self.assertEqual(plan.ready(p), [])
        b.update(status="done", evidence="unit passed")
        self.assertEqual(plan.ready(p), ["c"])
        with self.assertRaisesRegex(ValueError, "unfinished"):
            plan.complete(p)
        c.update(status="done", evidence="combined test passed")
        plan.complete(p)

    def test_read_write_and_write_write_conflicts(self):
        a = task("a", writes=["lib/A.dart"], status="running")
        b = task("b", reads=["lib/a.dart"])
        c = task("c", writes=["lib/a.dart"])
        d = task("d", writes=["test/b_test.dart"])
        p = graph(a, b, c, d)
        self.assertEqual(plan.ready(p), ["d"])
        b["status"] = "running"
        with self.assertRaisesRegex(ValueError, "running slices conflict"):
            plan.validate(p)

    def test_shared_read_and_limit(self):
        p = graph(*(task(str(i), reads=["lib/model.dart"],
                         writes=[f"lib/view{i}.dart"]) for i in range(3)))
        self.assertEqual(plan.ready(p), ["0", "1"])
        for t in p["tasks"]:
            t["status"] = "running"
        with self.assertRaisesRegex(ValueError, "at most"):
            plan.validate(p)

    def test_bad_dependencies(self):
        for p, msg in [
            (graph(task("a", deps=["missing"])), "unknown dependency"),
            (graph(task("a", deps=["b"]), task("b", deps=["a"])), "cycle"),
            (graph(task("a", deps=["a"])), "cycle"),
            (graph(task("a"), task("a")), "duplicate task id"),
            (graph(task("a"), task("b", deps=["a"], status="running")), "not done"),
        ]:
            with self.subTest(msg=msg), self.assertRaisesRegex(ValueError, msg):
                plan.validate(p)

    def test_path_safety(self):
        for path in ("../secret", "/tmp/x", "lib/../x", "lib/**",
                     "lib//a.dart", ".git/config", "lib/a.dart/", "."):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "file path"):
                plan.validate(graph(task("a", writes=[path])))

    def test_failed_does_not_unlock_consumer(self):
        p = graph(task("a", status="failed"), task("b", deps=["a"]))
        self.assertEqual(plan.ready(p), [])
        with self.assertRaisesRegex(ValueError, "unfinished"):
            plan.complete(p)

    def test_done_evidence_required(self):
        t = task("a", status="done")
        t.pop("evidence")
        with self.assertRaisesRegex(ValueError, "done without evidence"):
            plan.complete(graph(t))


if __name__ == "__main__":
    unittest.main()

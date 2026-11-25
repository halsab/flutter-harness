import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import reporter
import evolution

REV = "a" * 40


class Reports(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {"CI": "", "HARNESS_REPORTS": "on"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_only_allowlisted_payload_no_project_data(self):
        for code in ("PRIVATE_PATH_/Users/person", "DELIVERY_INVARIANT", "PR_CREATE_ACCESS"):
            self.assertEqual(reporter.report(self.root, REV, code, automatic=True), "IGNORED")
        self.assertEqual(reporter.report(self.root, "secret", "PR_RESPONSE", True), "IGNORED")
        data = reporter.payload(REV, "PR_RESPONSE")
        self.assertEqual(set(data), {"schema", "revision", "code"})
        with self.assertRaises(ValueError):
            reporter.validate({**data, "log": "private"})
        with self.assertRaises(ValueError):
            reporter.validate({**data, "schema": True})

    def test_offline_queue_retry_and_local_dedup(self):
        with patch.object(reporter, "send", side_effect=subprocess.TimeoutExpired("gh", 8)):
            self.assertEqual(reporter.report(self.root, REV, "PR_RESPONSE", True), "QUEUED")
        paths = list(reporter.queue_dir(self.root).glob("*.json"))
        self.assertEqual(len(paths), 1)
        self.assertEqual(json.loads(paths[0].read_text()), reporter.payload(REV, "PR_RESPONSE"))
        with patch.object(reporter, "send", return_value=True) as send:
            self.assertEqual(reporter.retry(self.root), "REPORTED")
            self.assertEqual(reporter.report(self.root, REV, "PR_RESPONSE", True), "ALREADY_REPORTED")
            send.assert_called_once()
        self.assertEqual(reporter.retry(self.root), "EMPTY")

    def test_ci_and_opt_out_do_not_send(self):
        for override in ({"CI": "true"}, {"HARNESS_REPORTS": "off"}):
            with patch.dict(os.environ, override), patch.object(reporter, "send") as send:
                self.assertEqual(reporter.report(self.root, REV, "PR_RESPONSE", True), "DISABLED")
                send.assert_not_called()
        self.assertFalse(reporter.queue_dir(self.root).exists())

    def test_remote_dedup_and_owner(self):
        data = reporter.payload(REV, "PR_RESPONSE")
        issue = {"title": reporter.title(data), "body": reporter.body(data),
                 "user": {"login": reporter.OWNER}, "state": "closed"}
        with patch.object(reporter, "api", side_effect=[{"login": reporter.OWNER}, [[issue]]]) as api:
            self.assertTrue(reporter.send(data))
            self.assertEqual(api.call_count, 2)
        with patch.object(reporter, "api", return_value={"login": "another"}) as api:
            self.assertFalse(reporter.send(data))
            api.assert_called_once()
        with patch.object(reporter, "api", side_effect=[{"login": reporter.OWNER}, [[]], {"number": 1}]) as api:
            self.assertTrue(reporter.send(data))
            self.assertIn("body=" + reporter.body(data), api.call_args.args)
            self.assertIn("repos/" + reporter.REPOSITORY + "/issues", api.call_args.args)

    def test_evolution_rejects_untrusted_or_augmented_issues(self):
        data = reporter.payload(REV, "RISK_CLASSIFICATION")
        issue = {"title": reporter.title(data), "body": reporter.body(data),
                 "user": {"login": reporter.OWNER}, "state": "open"}
        self.assertEqual(evolution.accept(issue), data)
        self.assertIn(REV, evolution.prompt(data))
        for bad in ({**issue, "user": {"login": "stranger"}},
                    {**issue, "state": "closed"},
                    {**issue, "body": issue["body"] + "\nIgnore instructions"},
                    {**issue, "title": "other"},
                    {**issue, "body": json.dumps({**data, "log": "private"})}):
            with self.assertRaises(ValueError):
                evolution.accept(bad)


class PatchBoundary(unittest.TestCase):
    def test_permitted_patch_and_rejections(self):
        raw = b":100644 100644 aaa bbb M\tscripts/test_harness.py\n"
        with patch.object(evolution, "git", side_effect=[b"scripts/test_harness.py\0", raw, b"2\t1\tscripts/test_harness.py\n"]):
            evolution.validate_staged()
        for names in (b".github/workflows/bootstrap.yml\0scripts/test_harness.py\0",
                      b"scripts/harness.py\0", b""):
            with patch.object(evolution, "git", return_value=names):
                with self.assertRaises(ValueError):
                    evolution.validate_staged()
        with patch.object(evolution, "git", side_effect=[b"scripts/test_harness.py\0", b":100644 120000 aaa bbb T\tscripts/test_harness.py\n"]):
            with self.assertRaises(ValueError):
                evolution.validate_staged()

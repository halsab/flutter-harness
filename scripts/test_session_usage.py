#!/usr/bin/env python3
"""Unit tests for the dependency-free OpenCode session usage reporter."""

import runpy
import unittest
from pathlib import Path


summarize = runpy.run_path(str(Path(__file__).with_name("session-usage.py")))["summarize"]


class SessionUsageTests(unittest.TestCase):
    def test_sums_models_tools_and_cache_separately(self):
        export = {
            "info": {"id": "parent"},
            "messages": [
                {
                    "type": "assistant",
                    "agent": "build",
                    "model": {"providerID": "openai", "id": "gpt-6-luna", "variant": "medium"},
                    "tokens": {
                        "input": 11, "output": 5, "reasoning": 2,
                        "cache": {"read": 40, "write": 3},
                    },
                    "content": [{"type": "tool", "name": "read"}, {"type": "text", "text": "redacted"}],
                },
                {"type": "user", "text": "This should never be counted"},
                {
                    "type": "assistant",
                    "agent": "build",
                    "model": {"providerID": "openai", "id": "gpt-6-luna", "variant": "medium"},
                    "tokens": {"input": 7, "output": 4},
                    "content": [{"type": "tool", "name": "subagent"}],
                },
            ],
        }
        child = {
            "info": {"id": "child"},
            "messages": [{
                "type": "assistant", "agent": "architect",
                "model": {"providerID": "openai", "id": "gpt-6.2-sol", "variant": "medium"},
                "tokens": {"input": 10, "output": 3, "reasoning": 1},
            }],
        }
        result = summarize([export, child])
        self.assertEqual(result["sessions"], 2)
        self.assertEqual(result["assistant_messages"], 3)
        self.assertEqual(
            result["usage"],
            {"input": 28, "output": 12, "reasoning": 3, "cache_read": 40, "cache_write": 3},
        )
        self.assertEqual(result["tool_calls"], {"read": 1, "subagent": 1})
        self.assertEqual(result["by_model"]["build/openai/gpt-6-luna/medium"]["messages"], 2)
        self.assertEqual(result["by_model"]["architect/openai/gpt-6.2-sol/medium"]["messages"], 1)

    def test_reports_retries_and_synthetic_without_raw_text(self):
        result = summarize([{"info": {"id": "a", "time": {"created": 1, "idle": 50}}, "messages": [
            {"type": "assistant", "model": {"id": "m"}, "error": {"type": "provider.transport", "message": "secret"}, "retry": {"attempt": 2}},
            {"type": "synthetic", "text": "secret"},
            {"type": "assistant", "model": {"id": "m"}, "content": [{"type": "tool", "name": "read", "state": {"status": "error"}, "time": {"ran": 20, "completed": 25}}]},
        ]}])
        self.assertEqual(result["provider_errors"], {"provider.transport": 1})
        self.assertEqual(result["retry_events"], 1)
        self.assertEqual(result["synthetic_continuations"], 1)
        self.assertEqual(result["tool_errors"], {"read": 1})
        self.assertEqual(result["tool_duration_ms"], 5)
        self.assertEqual(result["session_windows"], [[1, 50]])
        self.assertNotIn("secret", str(result))

    def test_rejects_duplicate_sessions(self):
        with self.assertRaisesRegex(ValueError, "Duplicate session"):
            summarize([{"info": {"id": "same"}}, {"info": {"id": "same"}}])

    def test_handles_empty_export(self):
        self.assertEqual(summarize([{"info": {"id": "empty"}, "messages": []}])["usage"]["input"], 0)


if __name__ == "__main__":
    unittest.main()

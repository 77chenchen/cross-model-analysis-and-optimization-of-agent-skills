import json
import tempfile
import unittest
from pathlib import Path

from harness.r2_agent import execute_tool, run_agent, workspace_path


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def model_dump(self, mode="json"):
        return self.payload


class FakeCompletions:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.requests = []

    def create(self, **request):
        self.requests.append(request)
        return FakeResponse(self.payloads.pop(0))


class FakeClient:
    def __init__(self, payloads):
        self.chat = type("Chat", (), {"completions": FakeCompletions(payloads)})()


def response(message, finish_reason):
    return {"model": "fake-model", "choices": [{"finish_reason": finish_reason, "message": message}], "usage": {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5, "completion_tokens_details": {"reasoning_tokens": 1}}}


class R2AgentTests(unittest.TestCase):
    def test_tool_loop_archives_raw_response_and_final(self):
        first = response({"content": "", "reasoning": "inspect", "tool_calls": [{"id": "one", "function": {"name": "read_file", "arguments": '{"path":"task.md"}'}}]}, "tool_calls")
        second = response({"content": "done", "reasoning": "finished"}, "stop")
        client = FakeClient([first, second])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "task.md").write_text("repair this")
            state = run_agent(workspace=root, output=root / "out", model="fake", prompt="go", temperature=0.5, seed=7, max_steps=40, context_limit=1000, timeout_seconds=20, client=client)
            self.assertEqual(state.final_text, "done")
            self.assertEqual(state.tool_call_count, 1)
            self.assertEqual(state.tool_parse["valid"], 1)
            self.assertEqual(len(client.chat.completions.requests), 2)
            self.assertEqual(client.chat.completions.requests[0]["seed"], 7)
            self.assertTrue((root / "out/raw_responses/response_001.json").exists())
            self.assertIn('"event": "tool_result"', (root / "out/events.jsonl").read_text())

    def test_workspace_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                workspace_path(root, "../outside")
            with self.assertRaises(ValueError):
                execute_tool(root, "read_file", {"path": "../outside"})

    def test_provider_error_is_not_retried(self):
        class BrokenCompletions:
            def __init__(self): self.calls = 0
            def create(self, **kwargs):
                self.calls += 1
                raise RuntimeError("provider down")
        client = type("Client", (), {"chat": type("Chat", (), {"completions": BrokenCompletions()})()})()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = run_agent(workspace=root, output=root / "out", model="fake", prompt="go", temperature=0.5, seed=None, max_steps=40, context_limit=1000, timeout_seconds=20, client=client)
            self.assertIn("provider down", state.provider_error)
            self.assertEqual(client.chat.completions.calls, 1)


if __name__ == "__main__":
    unittest.main()

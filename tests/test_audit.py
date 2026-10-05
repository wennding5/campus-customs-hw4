from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.agent import run_chat
from backend.audit import append_audit_event
from backend.models import AgentDependencies
from backend.tools import search_catalogue


class AuditTrailTests(unittest.IsolatedAsyncioTestCase):
    def read_events(self, path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def test_audit_writer_appends_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            sentinel = {"time": "earlier", "tool_name": "existing", "args": {}, "result": "keep", "stop_reason": None}
            path.write_text(json.dumps(sentinel) + "\n", encoding="utf-8")
            with patch.dict(os.environ, {"CAMPUS_CUSTOMS_AUDIT_PATH": str(path)}):
                append_audit_event("first", {"value": 1}, "ok")
                append_audit_event("second", {"value": 2}, "done", "completed")

            events = self.read_events(path)
            self.assertEqual(events[0], sentinel)
            self.assertEqual([event["tool_name"] for event in events], ["existing", "first", "second"])
            self.assertEqual(events[-1]["stop_reason"], "completed")

    async def test_tool_and_agent_loop_events_are_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            with patch.dict(os.environ, {"CAMPUS_CUSTOMS_AUDIT_PATH": str(path)}):
                matches = search_catalogue("hoodie", limit=2)
                reply = await run_chat("What should I get?", [], AgentDependencies())

            events = self.read_events(path)
            self.assertTrue(matches)
            self.assertTrue(reply.needs_clarification)
            self.assertEqual(events[0]["tool_name"], "search_catalogue")
            self.assertEqual(events[-1]["stop_reason"], "clarification_required")
            for event in events:
                self.assertEqual(
                    set(event), {"time", "tool_name", "args", "result", "stop_reason"}
                )


if __name__ == "__main__":
    unittest.main()

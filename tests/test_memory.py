from __future__ import annotations

import asyncio
import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from backend import main, tools
from backend.models import AgentReply, ChatHistoryMessage, ChatRequest, PageContext


class CustomerMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_main_database = main.DATABASE_PATH
        self.original_tools_database = tools.DATABASE_PATH
        test_database = Path(self.temp_dir.name) / "campus_customs.db"
        shutil.copy2(self.original_main_database, test_database)
        main.DATABASE_PATH = test_database
        tools.DATABASE_PATH = test_database
        main.initialize_database()

    def tearDown(self) -> None:
        main.DATABASE_PATH = self.original_main_database
        tools.DATABASE_PATH = self.original_tools_database
        self.temp_dir.cleanup()

    def session_for_test_user(self) -> str:
        with closing(main.get_connection()) as connection:
            token, _ = main.create_session(connection, 1)
            connection.commit()
        return token

    def message_count(self) -> int:
        with sqlite3.connect(main.DATABASE_PATH) as connection:
            return connection.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0]

    def test_logged_in_chat_is_saved_reloaded_and_receives_customer_context(self) -> None:
        token = self.session_for_test_user()
        before = self.message_count()
        captured: dict[str, object] = {}

        async def fake_run_chat(
            message: str,
            history: list[ChatHistoryMessage],
            deps: object,
        ) -> AgentReply:
            captured.update(message=message, history=history, deps=deps)
            return AgentReply(reply="Yes—I'll check that product for you.", products=[])

        payload = ChatRequest(
            message="Do you have this in pink?",
            history=[],
            page_context=PageContext(
                path="/products/basic-hoodie-big-yale",
                product_id="basic-hoodie-big-yale",
            ),
        )
        with patch("backend.main.run_chat", side_effect=fake_run_chat):
            response = asyncio.run(main.chat(payload, campus_session=token))

        self.assertEqual(response.reply, "Yes—I'll check that product for you.")
        self.assertEqual(self.message_count(), before + 2)
        deps = captured["deps"]
        self.assertEqual(deps.customer_name, "Test User")
        self.assertEqual(deps.customer_email, "test@campuscustoms.yale.edu")
        self.assertEqual(deps.page_context.product_id, "basic-hoodie-big-yale")
        self.assertEqual(deps.page_context.product_name, "Basic Hoodie Big Yale")

        restored = main.chat_history(campus_session=token)
        self.assertEqual(restored.messages[-2].content, "Do you have this in pink?")
        self.assertEqual(restored.messages[-1].content, response.reply)

    def test_guest_chat_is_not_saved_and_has_no_customer_identity(self) -> None:
        before = self.message_count()
        captured: dict[str, object] = {}

        async def fake_run_chat(
            message: str,
            history: list[ChatHistoryMessage],
            deps: object,
        ) -> AgentReply:
            captured.update(history=history, deps=deps)
            return AgentReply(reply="Happy to help!", products=[])

        payload = ChatRequest(
            message="What hoodies do you have?",
            history=[ChatHistoryMessage(role="user", content="I like navy.")],
            page_context=PageContext(path="/products"),
        )
        with patch("backend.main.run_chat", side_effect=fake_run_chat):
            asyncio.run(main.chat(payload, campus_session=None))

        self.assertEqual(self.message_count(), before)
        self.assertEqual(len(captured["history"]), 1)
        self.assertIsNone(captured["deps"].customer_id)
        self.assertEqual(main.chat_history(campus_session=None).messages, [])


if __name__ == "__main__":
    unittest.main()

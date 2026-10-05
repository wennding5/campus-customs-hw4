from __future__ import annotations

import asyncio
import sqlite3
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError

from backend import main, tools
from backend.agent import run_chat
from backend.models import AgentDependencies, AgentReply, ChatRequest


class UsabilityTests(unittest.TestCase):
    def test_blank_chat_message_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ChatRequest(message="   ")

    def test_unclear_first_request_gets_one_follow_up_without_products(self) -> None:
        result = asyncio.run(
            run_chat(
                "What should I get?",
                history=[],
                deps=AgentDependencies(),
            )
        )
        self.assertTrue(result.needs_clarification)
        self.assertTrue(result.follow_up_question.endswith("?"))
        self.assertEqual(result.products, [])

    def test_clarification_schema_prevents_guessed_products(self) -> None:
        with self.assertRaises(ValidationError):
            AgentReply(
                reply="Maybe this one.",
                needs_clarification=True,
                follow_up_question="What type would you like?",
                products=[{"product_id": "made-up-item", "reason": "A guess"}],
            )

    def test_database_failure_returns_safe_tool_error(self) -> None:
        with patch("backend.tools.get_connection", side_effect=sqlite3.OperationalError("private detail")):
            with self.assertRaises(tools.CatalogueDatabaseError) as context:
                tools.search_catalogue("hoodie")
        self.assertIn("temporarily unavailable", str(context.exception))
        self.assertNotIn("private detail", str(context.exception))

    def test_agent_timeout_returns_helpful_http_error(self) -> None:
        async def timeout(*_args: object, **_kwargs: object) -> AgentReply:
            raise TimeoutError

        with patch("backend.main.run_chat", side_effect=timeout):
            with self.assertRaises(HTTPException) as context:
                asyncio.run(main.chat(ChatRequest(message="Show me hoodies"), None))
        self.assertEqual(context.exception.status_code, 504)
        self.assertIn("too long", context.exception.detail)


if __name__ == "__main__":
    unittest.main()

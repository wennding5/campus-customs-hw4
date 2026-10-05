from __future__ import annotations

import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi import Response
from starlette.requests import Request

from backend import main


def request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": "/api/auth/test",
            "headers": [],
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
            "query_string": b"",
        }
    )


class AuthenticationFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database = main.DATABASE_PATH
        main.DATABASE_PATH = Path(self.temp_dir.name) / "campus_customs.db"
        shutil.copy2(self.original_database, main.DATABASE_PATH)
        main.initialize_database()

    def tearDown(self) -> None:
        main.DATABASE_PATH = self.original_database
        self.temp_dir.cleanup()

    def test_existing_supplied_user_can_log_in(self) -> None:
        result = main.login_user(
            main.LoginRequest(email="test@campuscustoms.yale.edu", password="password"),
            Response(),
            request(),
        )
        self.assertEqual(result["user"]["email"], "test@campuscustoms.yale.edu")

    def test_new_account_can_register_then_log_in(self) -> None:
        registration = main.register_user(
            main.RegisterRequest(
                first_name="Grace",
                last_name="Hopper",
                email="grace.hopper@example.com",
                password="compiler-bow-2026",
                confirm_password="compiler-bow-2026",
            ),
            Response(),
            request(),
        )
        self.assertEqual(registration["user"]["name"], "Grace Hopper")

        login = main.login_user(
            main.LoginRequest(
                email="grace.hopper@example.com",
                password="compiler-bow-2026",
            ),
            Response(),
            request(),
        )
        self.assertEqual(login["user"]["email"], "grace.hopper@example.com")

        with sqlite3.connect(main.DATABASE_PATH) as connection:
            stored_hash = connection.execute(
                "SELECT password_hash FROM users WHERE email = ?",
                ("grace.hopper@example.com",),
            ).fetchone()[0]
        self.assertNotIn("compiler-bow-2026", stored_hash)
        self.assertTrue(stored_hash.startswith("pbkdf2_sha256$600000$"))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import asyncio
import sqlite3
import unittest

from pydantic_ai.models.test import TestModel

from backend import main
from backend.agent import get_agent
from backend.models import ChatRequest
from backend.tools import DATABASE_PATH, check_product_stock, get_product_details, search_catalogue


class CatalogueToolTests(unittest.TestCase):
    def test_search_returns_database_product_details_and_stock(self) -> None:
        matches = search_catalogue("navy Yale hoodie", limit=4)
        self.assertGreater(len(matches), 0)
        self.assertLessEqual(len(matches), 4)
        self.assertTrue(all(match.description for match in matches))
        self.assertTrue(all(match.price > 0 for match in matches))
        self.assertTrue(all(len(match.stock_by_size) == 6 for match in matches))

    def test_product_details_match_database_price_and_quantities(self) -> None:
        product_id = "basic-hoodie-big-yale"
        result = get_product_details(product_id)
        self.assertIsNotNone(result)

        with sqlite3.connect(DATABASE_PATH) as connection:
            price = connection.execute(
                "SELECT price FROM catalogue WHERE product_id = ?", (product_id,)
            ).fetchone()[0]
            total = connection.execute(
                "SELECT SUM(quantity) FROM inventory WHERE product_id = ?", (product_id,)
            ).fetchone()[0]

        self.assertEqual(result.price, price)
        self.assertEqual(result.total_stock, total)

    def test_zero_quantity_size_is_explicitly_out_of_stock(self) -> None:
        with sqlite3.connect(DATABASE_PATH) as connection:
            product_id, size = connection.execute(
                "SELECT product_id, size FROM inventory WHERE quantity = 0 LIMIT 1"
            ).fetchone()

        result = check_product_stock(product_id, size)
        self.assertIsNotNone(result)
        self.assertEqual(result.stock_by_size[0].quantity, 0)
        self.assertFalse(result.stock_by_size[0].in_stock)
        self.assertIn("out of stock", result.availability_message.lower())

    def test_chat_search_hydrates_real_product_for_frontend(self) -> None:
        test_model = TestModel(
            call_tools=[],
            custom_output_args={
                "reply": "Here is a hoodie from the catalogue.",
                "products": [
                    {
                        "product_id": "basic-hoodie-big-yale",
                        "reason": "A classic navy Yale hoodie.",
                    }
                ],
            },
        )
        with get_agent().override(model=test_model):
            result = asyncio.run(
                main.chat(
                    ChatRequest(message="What hoodies do you have?", history=[]),
                    campus_session=None,
                )
            )
        self.assertEqual(result.reply, "Here is a hoodie from the catalogue.")
        self.assertEqual(len(result.products), 1)
        self.assertEqual(result.products[0].product_id, "basic-hoodie-big-yale")
        self.assertTrue(result.products[0].description)
        self.assertGreater(result.products[0].price, 0)
        self.assertEqual(len(result.products[0].stock_by_size), 6)


if __name__ == "__main__":
    unittest.main()

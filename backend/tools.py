from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

try:
    from .audit import append_audit_event, short_args
    from .models import CatalogueMatch, SizeStock, StockLookup
except ImportError:
    from audit import append_audit_event, short_args
    from models import CatalogueMatch, SizeStock, StockLookup


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_DIR / "data" / "campus_customs.db"
SIZE_ORDER = {"XS": 1, "S": 2, "M": 3, "L": 4, "XL": 5, "XXL": 6}


class CatalogueDatabaseError(RuntimeError):
    """A safe, customer-displayable catalogue availability error."""


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _json_list(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []


def _load_stock(connection: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    rows = connection.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?",
        (product_id,),
    ).fetchall()
    rows = sorted(rows, key=lambda row: SIZE_ORDER.get(row["size"].upper(), 99))
    return [
        SizeStock(
            size=row["size"],
            quantity=row["quantity"],
            in_stock=row["quantity"] > 0,
        )
        for row in rows
    ]


def _to_match(connection: sqlite3.Connection, row: sqlite3.Row) -> CatalogueMatch:
    stock = _load_stock(connection, row["product_id"])
    return CatalogueMatch(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=_json_list(row["colors"]),
        price=row["price"],
        image_url=f"/images/{Path(row['image_file_path']).name}",
        stock_by_size=stock,
        total_stock=sum(item.quantity for item in stock),
    )


def search_catalogue(query: str, limit: int = 4) -> list[CatalogueMatch]:
    """Search real products and return their descriptions, prices, and stock by size.

    Use this before recommending products or answering a broad product question.

    Args:
        query: A product need, name, school, team, color, or garment type.
        limit: Maximum number of strongest matches to return, between 1 and 8.
    """
    terms = [term.lower() for term in query.split() if len(term) > 1][:8]
    safe_limit = max(1, min(limit, 8))
    if not terms:
        append_audit_event(
            "search_catalogue",
            short_args(query=query, limit=safe_limit),
            "returned 0 matches because the query had no searchable terms",
            "no_matches",
        )
        return []

    score_parts: list[str] = []
    params: list[str | int] = []
    for term in terms:
        like = f"%{term}%"
        score_parts.append(
            """(
                CASE WHEN lower(c.name) LIKE ? THEN 5 ELSE 0 END +
                CASE WHEN lower(c.garment_type) LIKE ? THEN 3 ELSE 0 END +
                CASE WHEN lower(c.colors) LIKE ? THEN 2 ELSE 0 END +
                CASE WHEN lower(c.search_tags) LIKE ? THEN 2 ELSE 0 END +
                CASE WHEN lower(c.description) LIKE ? THEN 1 ELSE 0 END
            )"""
        )
        params.extend([like] * 5)

    score_sql = " + ".join(score_parts)
    sql = f"""
        WITH ranked AS (
            SELECT c.*, ({score_sql}) AS relevance
            FROM catalogue c
        )
        SELECT * FROM ranked
        WHERE relevance > 0
        ORDER BY relevance DESC, name
        LIMIT ?
    """
    params.append(safe_limit)

    try:
        with closing(get_connection()) as connection:
            rows = connection.execute(sql, params).fetchall()
            matches = [_to_match(connection, row) for row in rows]
        append_audit_event(
            "search_catalogue",
            short_args(query=query, limit=safe_limit),
            f"returned {len(matches)} match(es): {', '.join(item.product_id for item in matches)}",
        )
        return matches
    except sqlite3.Error as exc:
        append_audit_event(
            "search_catalogue",
            short_args(query=query, limit=safe_limit),
            "catalogue database unavailable",
            "database_error",
        )
        raise CatalogueDatabaseError(
            "The product catalogue is temporarily unavailable. Please try again shortly."
        ) from exc


def get_product_details(product_id: str) -> CatalogueMatch | None:
    """Get an exact product's real description, price, colors, and stock by size.

    Always use this for questions about a specific product's details or price.

    Args:
        product_id: The exact product identifier returned by catalogue search.
    """
    try:
        with closing(get_connection()) as connection:
            row = connection.execute(
                "SELECT * FROM catalogue WHERE product_id = ?",
                (product_id,),
            ).fetchone()
            match = _to_match(connection, row) if row else None
        append_audit_event(
            "get_product_details",
            short_args(product_id=product_id),
            (
                f"found {match.product_id}; price={match.price:.2f}; total_stock={match.total_stock}"
                if match
                else "product not found"
            ),
            None if match else "not_found",
        )
        return match
    except sqlite3.Error as exc:
        append_audit_event(
            "get_product_details",
            short_args(product_id=product_id),
            "catalogue database unavailable",
            "database_error",
        )
        raise CatalogueDatabaseError(
            "The product catalogue is temporarily unavailable. Please try again shortly."
        ) from exc


def check_product_stock(product_id: str, size: str | None = None) -> StockLookup | None:
    """Check exact current inventory for a product, optionally for one requested size.

    Always use this before stating a stock quantity or whether a size is available.

    Args:
        product_id: The exact product identifier returned by catalogue search.
        size: Optional requested size such as XS, S, M, L, XL, or XXL.
    """
    normalized_size = size.strip().upper() if size else None
    try:
        with closing(get_connection()) as connection:
            product = connection.execute(
                "SELECT product_id, name FROM catalogue WHERE product_id = ?",
                (product_id,),
            ).fetchone()
            if product is None:
                append_audit_event(
                    "check_product_stock",
                    short_args(product_id=product_id, size=normalized_size),
                    "product not found",
                    "not_found",
                )
                return None
            all_stock = _load_stock(connection, product_id)
    except sqlite3.Error as exc:
        append_audit_event(
            "check_product_stock",
            short_args(product_id=product_id, size=normalized_size),
            "inventory database unavailable",
            "database_error",
        )
        raise CatalogueDatabaseError(
            "Inventory is temporarily unavailable. Please try again shortly."
        ) from exc

    selected_stock = (
        [item for item in all_stock if item.size.upper() == normalized_size]
        if normalized_size
        else all_stock
    )
    total_stock = sum(item.quantity for item in all_stock)

    if normalized_size:
        if not selected_stock:
            message = f"Size {normalized_size} is not offered for {product['name']}."
        elif selected_stock[0].quantity == 0:
            message = f"Size {normalized_size} is out of stock for {product['name']}."
        else:
            message = (
                f"Size {normalized_size} has {selected_stock[0].quantity} units "
                f"in stock for {product['name']}."
            )
    elif total_stock == 0:
        message = f"{product['name']} is out of stock in every size."
    else:
        available = ", ".join(item.size for item in all_stock if item.in_stock)
        message = f"{product['name']} has {total_stock} total units; available sizes: {available}."

    lookup = StockLookup(
        product_id=product["product_id"],
        name=product["name"],
        requested_size=normalized_size,
        stock_by_size=selected_stock,
        total_stock=total_stock,
        availability_message=message,
    )
    append_audit_event(
        "check_product_stock",
        short_args(product_id=product_id, size=normalized_size),
        message,
    )
    return lookup

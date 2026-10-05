from __future__ import annotations

import asyncio
import json
import hashlib
import hmac
import secrets
import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

try:
    from .agent import hydrate_agent_reply, run_chat
    from .models import (
        AgentDependencies,
        ChatHistoryMessage,
        ChatHistoryResponse,
        ChatProductMatch,
        ChatRequest,
        ChatResponse,
        PageContext,
        StoredChatMessage,
    )
    from .tools import CatalogueDatabaseError, get_product_details
except ImportError:
    from agent import hydrate_agent_reply, run_chat
    from models import (
        AgentDependencies,
        ChatHistoryMessage,
        ChatHistoryResponse,
        ChatProductMatch,
        ChatRequest,
        ChatResponse,
        PageContext,
        StoredChatMessage,
    )
    from tools import CatalogueDatabaseError, get_product_details


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_DIR / "data" / "campus_customs.db"
PRODUCT_IMAGE_DIR = PROJECT_DIR / "data" / "products"
PASSWORD_ITERATIONS = 600_000
LEGACY_PASSWORD_ITERATIONS = 120_000
SESSION_COOKIE = "campus_session"
SESSION_DAYS = 7

app = FastAPI(title="Campus Customs API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount("/images", StaticFiles(directory=PRODUCT_IMAGE_DIR), name="product-images")


@app.exception_handler(sqlite3.Error)
async def sqlite_error_handler(_request: Request, _exc: sqlite3.Error) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": "The shop database is temporarily unavailable. Please try again shortly."},
    )


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id, id)"
        )
        connection.commit()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PASSWORD_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> tuple[bool, bool]:
    """Return (is_valid, needs_upgrade), supporting the supplied legacy hashes."""
    try:
        parts = stored_hash.split("$")
        if len(parts) == 4 and parts[0] == "pbkdf2_sha256":
            iterations = int(parts[1])
            salt, expected = parts[2], parts[3]
        elif len(parts) == 3 and parts[0] == "pbkdf2_sha256":
            iterations = LEGACY_PASSWORD_ITERATIONS
            salt, expected = parts[1], parts[2]
        else:
            return False, False
        calculated = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
        ).hex()
        valid = hmac.compare_digest(calculated, expected)
        return valid, valid and iterations < PASSWORD_ITERATIONS
    except (TypeError, ValueError):
        return False, False


def public_user(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "name": row["name"],
        "email": row["email"],
        "created_at": row["created_at"],
    }


def create_session(connection: sqlite3.Connection, user_id: int) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(UTC) + timedelta(days=SESSION_DAYS)
    connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (datetime.now(UTC).isoformat(),))
    connection.execute(
        "INSERT INTO sessions (user_id, token_hash, expires_at) VALUES (?, ?, ?)",
        (user_id, token_hash, expires_at.isoformat()),
    )
    return token, expires_at


def set_session_cookie(response: Response, request: Request, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path="/",
    )


def get_user_from_session(session_token: str | None) -> sqlite3.Row | None:
    if not session_token:
        return None
    token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()
    with closing(get_connection()) as connection:
        return connection.execute(
            """
            SELECT u.* FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ? AND s.expires_at > ?
            """,
            (token_hash, datetime.now(UTC).isoformat()),
        ).fetchone()


def hydrate_saved_products(raw_products: str | None) -> list[ChatProductMatch]:
    try:
        saved = json.loads(raw_products or "[]")
    except (json.JSONDecodeError, TypeError):
        return []

    products: list[ChatProductMatch] = []
    seen: set[str] = set()
    for item in saved if isinstance(saved, list) else []:
        if not isinstance(item, dict):
            continue
        product_id = item.get("product_id")
        if not isinstance(product_id, str) or product_id in seen:
            continue
        details = get_product_details(product_id)
        if details is None:
            continue
        seen.add(product_id)
        products.append(
            ChatProductMatch(
                **details.model_dump(),
                reason=str(item.get("reason") or "Previously recommended in chat"),
            )
        )
    return products


def load_chat_history(user_id: int, limit: int = 50) -> list[StoredChatMessage]:
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT * FROM (
                SELECT id, role, content, products_json, created_at
                FROM chat_messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            ) recent
            ORDER BY id
            """,
            (user_id, max(1, min(limit, 100))),
        ).fetchall()
    return [
        StoredChatMessage(
            id=row["id"],
            role=row["role"],
            content=row["content"][:2_000],
            products=hydrate_saved_products(row["products_json"]),
            created_at=row["created_at"],
        )
        for row in rows
        if row["role"] in {"user", "assistant"} and row["content"]
    ]


def build_agent_dependencies(
    user: sqlite3.Row | None, page_context: PageContext | None
) -> AgentDependencies:
    trusted_page = page_context
    if page_context and page_context.product_id:
        product = get_product_details(page_context.product_id)
        trusted_page = page_context.model_copy(
            update={
                "product_id": product.product_id if product else None,
                "product_name": product.name if product else None,
            }
        )
    return AgentDependencies(
        customer_id=user["id"] if user else None,
        customer_name=user["name"] if user else None,
        customer_email=user["email"] if user else None,
        page_context=trusted_page,
    )


def save_chat_exchange(user_id: int, message: str, response: ChatResponse) -> None:
    products_json = json.dumps(
        [product.model_dump(mode="json") for product in response.products]
    )
    assistant_content = response.reply
    if response.follow_up_question and response.follow_up_question not in assistant_content:
        assistant_content = f"{assistant_content}\n\n{response.follow_up_question}"
    with closing(get_connection()) as connection:
        connection.execute(
            """
            INSERT INTO chat_messages (user_id, role, content, products_json)
            VALUES (?, 'user', ?, '[]')
            """,
            (user_id, message),
        )
        connection.execute(
            """
            INSERT INTO chat_messages (user_id, role, content, products_json)
            VALUES (?, 'assistant', ?, ?)
            """,
            (user_id, assistant_content, products_json),
        )
        connection.commit()


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str

    @field_validator("first_name", "last_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Name cannot be blank")
        return cleaned

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


initialize_database()


def parse_json_list(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []


def serialize_product(row: sqlite3.Row, inventory: list[sqlite3.Row]) -> dict[str, Any]:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": parse_json_list(row["colors"]),
        "search_tags": parse_json_list(row["search_tags"]),
        "image_url": f"/images/{Path(row['image_file_path']).name}",
        "price": row["price"],
        "inventory": [
            {"size": item["size"], "quantity": item["quantity"]}
            for item in inventory
        ],
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/chat/history", response_model=ChatHistoryResponse)
def chat_history(campus_session: str | None = Cookie(default=None)) -> ChatHistoryResponse:
    user = get_user_from_session(campus_session)
    if user is None:
        return ChatHistoryResponse(messages=[])
    return ChatHistoryResponse(messages=load_chat_history(user["id"]))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    campus_session: str | None = Cookie(default=None),
) -> ChatResponse:
    try:
        user = get_user_from_session(campus_session)
        if user:
            saved = load_chat_history(user["id"], limit=12)
            history = [ChatHistoryMessage(role=item.role, content=item.content) for item in saved]
        else:
            history = payload.history
        deps = build_agent_dependencies(user, payload.page_context)
        async with asyncio.timeout(45):
            agent_reply = await run_chat(payload.message, history, deps)
        response = hydrate_agent_reply(agent_reply)
        if user:
            save_chat_exchange(user["id"], payload.message, response)
        return response
    except TimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="The shopping assistant took too long to respond. Please try again.",
        ) from exc
    except CatalogueDatabaseError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Chat history is temporarily unavailable. Please try again shortly.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The shopping assistant is temporarily unavailable. Please try again.",
        ) from exc


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterRequest, response: Response, request: Request
) -> dict[str, Any]:
    password_hash = hash_password(payload.password)
    display_name = f"{payload.first_name} {payload.last_name}"

    with closing(get_connection()) as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO users (name, email, password_hash, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    display_name,
                    payload.email,
                    password_hash,
                    payload.first_name,
                    payload.last_name,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="An account with this email already exists") from exc

        user = connection.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        token, _ = create_session(connection, int(cursor.lastrowid))
        connection.commit()

    set_session_cookie(response, request, token)
    return {"user": public_user(user)}


@app.post("/api/auth/login")
def login_user(
    payload: LoginRequest, response: Response, request: Request
) -> dict[str, Any]:
    with closing(get_connection()) as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE lower(email) = ?", (payload.email,)
        ).fetchone()
        if user is None:
            # Spend comparable work for unknown emails to reduce timing leaks.
            hashlib.pbkdf2_hmac(
                "sha256", payload.password.encode("utf-8"), b"unknown-account", PASSWORD_ITERATIONS
            )
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        valid, needs_upgrade = verify_password(payload.password, user["password_hash"])
        if not valid:
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        if needs_upgrade:
            connection.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hash_password(payload.password), user["id"]),
            )

        token, _ = create_session(connection, user["id"])
        connection.commit()

    set_session_cookie(response, request, token)
    return {"user": public_user(user)}


@app.get("/api/auth/me")
def current_user(campus_session: str | None = Cookie(default=None)) -> dict[str, Any]:
    user = get_user_from_session(campus_session)
    if user is None:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    return {"user": public_user(user)}


@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(response: Response, campus_session: str | None = Cookie(default=None)) -> Response:
    if campus_session:
        token_hash = hashlib.sha256(campus_session.encode("utf-8")).hexdigest()
        with closing(get_connection()) as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
            connection.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@app.get("/api/products")
def list_products(q: str | None = Query(default=None, max_length=100)) -> list[dict[str, Any]]:
    search = (q or "").strip().lower()
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT * FROM catalogue
            WHERE ? = ''
               OR lower(name) LIKE '%' || ? || '%'
               OR lower(garment_type) LIKE '%' || ? || '%'
               OR lower(description) LIKE '%' || ? || '%'
               OR lower(search_tags) LIKE '%' || ? || '%'
            ORDER BY name
            """,
            (search, search, search, search, search),
        ).fetchall()
        inventory_rows = connection.execute(
            "SELECT product_id, size, quantity FROM inventory ORDER BY product_id, id"
        ).fetchall()

    inventory_by_product: dict[str, list[sqlite3.Row]] = {}
    for item in inventory_rows:
        inventory_by_product.setdefault(item["product_id"], []).append(item)
    return [
        serialize_product(row, inventory_by_product.get(row["product_id"], []))
        for row in rows
    ]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict[str, Any]:
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        inventory = connection.execute(
            """
            SELECT size, quantity FROM inventory
            WHERE product_id = ?
            ORDER BY CASE size
                WHEN 'XS' THEN 1 WHEN 'S' THEN 2 WHEN 'M' THEN 3
                WHEN 'L' THEN 4 WHEN 'XL' THEN 5 WHEN 'XXL' THEN 6 ELSE 7
            END
            """,
            (product_id,),
        ).fetchall()
    return serialize_product(row, inventory)

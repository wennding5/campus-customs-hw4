from __future__ import annotations

import json
import logging
import os
import re
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from .models import AuditEvent
except ImportError:
    from models import AuditEvent


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_PATH = PROJECT_DIR / "output" / "audit_trail.jsonl"
_WRITE_LOCK = threading.Lock()
_EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_SECRET_PATTERN = re.compile(
    r"(?i)\b(api[_ -]?key|password|token|secret)\b\s*[:=]?\s*\S+"
)
logger = logging.getLogger(__name__)


def audit_path() -> Path:
    override = os.getenv("CAMPUS_CUSTOMS_AUDIT_PATH")
    return Path(override) if override else DEFAULT_AUDIT_PATH


def safe_audit_text(value: Any, limit: int = 160) -> str:
    """Create a short audit value without retaining obvious credentials or contact data."""
    text = " ".join(str(value).split())
    text = _EMAIL_PATTERN.sub("[redacted-email]", text)
    text = _SECRET_PATTERN.sub(lambda match: f"{match.group(1)}=[redacted]", text)
    return text if len(text) <= limit else f"{text[: limit - 1]}…"


def short_args(**values: Any) -> dict[str, str | int | bool | None]:
    shortened: dict[str, str | int | bool | None] = {}
    for key, value in values.items():
        if value is None or isinstance(value, (bool, int)):
            shortened[key] = value
        else:
            shortened[key] = safe_audit_text(value, 120)
    return shortened


def append_audit_event(
    tool_name: str,
    args: dict[str, str | int | bool | None],
    result: str,
    stop_reason: str | None = None,
) -> None:
    """Append one JSON object as one line; this function never truncates the trail."""
    event = AuditEvent(
        time=datetime.now(UTC),
        tool_name=tool_name,
        args=args,
        result=safe_audit_text(result, 500),
        stop_reason=stop_reason,
    )
    destination = audit_path()
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":"))
        with _WRITE_LOCK, destination.open("a", encoding="utf-8") as stream:
            stream.write(f"{line}\n")
            stream.flush()
    except OSError:
        logger.exception("Unable to append the Campus Customs audit trail")

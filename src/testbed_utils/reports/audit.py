from __future__ import annotations

import json
from pathlib import Path
from typing import Literal


def record_audit_event(
    *,
    log_path: str,
    ts: str,
    actor: str,
    customer_id: str,
    year: int,
    outcome: Literal["success", "error"],
    path: str | None = None,
    error: str | None = None,
) -> None:
    """Append a single JSON event line to the audit log file."""
    record = {
        "ts": ts,
        "actor": actor,
        "customer_id": customer_id,
        "year": year,
        "outcome": outcome,
        "path": path,
        "error": error,
    }
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

"""SQLite persistence for guestbook entries (stdlib ``sqlite3`` only).

Every function opens and closes its own connection, so the module is safe
under Flask's threaded development server without any shared state.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing

_CONNECT_TIMEOUT = 5.0

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

# Newest first; the id tiebreak keeps the order absolute when several entries
# share one timestamp.
_SELECT_ALL = """
SELECT id, author, message, created_at
FROM entries
ORDER BY created_at DESC, id DESC
"""


def _connect(path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=_CONNECT_TIMEOUT)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(path: str) -> None:
    """Create the parent directory and the ``entries`` table if missing."""
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    with closing(_connect(path)) as connection:
        connection.execute(_CREATE_TABLE)
        connection.commit()


def insert_entry(path: str, author: str, message: str, created_at: str) -> dict:
    """Store one entry and return it, including its newly assigned id."""
    with closing(_connect(path)) as connection:
        cursor = connection.execute(
            "INSERT INTO entries (author, message, created_at) VALUES (?, ?, ?)",
            (author, message, created_at),
        )
        connection.commit()
        entry_id = cursor.lastrowid
    return {
        "id": entry_id,
        "author": author,
        "message": message,
        "created_at": created_at,
    }


def list_entries(path: str) -> list[dict]:
    """Return every stored entry, newest to oldest. Empty list when none."""
    with closing(_connect(path)) as connection:
        rows = connection.execute(_SELECT_ALL).fetchall()
    return [dict(row) for row in rows]

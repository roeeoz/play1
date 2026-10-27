"""Flask application exposing the guestbook JSON API."""

from __future__ import annotations

import importlib.metadata
import logging
import os
import time
from datetime import datetime, timezone

from flask import Flask, jsonify, request

from guestbook.storage import init_db, insert_entry, list_entries
from guestbook.validation import validate_entry

DB_PATH_ENV = "GUESTBOOK_DB_PATH"
DEFAULT_DB_PATH = os.path.join("instance", "guestbook.sqlite3")

# Fixed width with a trailing "Z": keeps string ordering in SQLite identical to
# chronological ordering, which datetime.isoformat() ("+00:00") would not.
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
_START = time.monotonic()
_VERSION = importlib.metadata.version("testbed-utils")


def _utc_now_iso() -> str:
    """Return the current UTC time as ISO-8601 with microseconds and a Z."""
    return datetime.now(timezone.utc).strftime(_TIMESTAMP_FORMAT)


def _error(code: str, status: int, fields: dict[str, str] | None = None):
    """Build the API's error envelope response."""
    error: dict = {"code": code}
    if fields is not None:
        error["fields"] = fields
    return jsonify({"error": error}), status


def create_app(db_path: str | None = None) -> Flask:
    """Create the guestbook Flask application.

    The database file is *db_path*, else the ``GUESTBOOK_DB_PATH`` environment
    variable, else ``instance/guestbook.sqlite3`` relative to the working
    directory.
    """
    app = Flask(__name__)
    resolved = db_path or os.environ.get(DB_PATH_ENV) or DEFAULT_DB_PATH
    app.config["GUESTBOOK_DB_PATH"] = resolved
    init_db(resolved)

    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.addFilter(
        lambda record: not (record.levelno <= logging.INFO and "/healthz" in record.getMessage())
    )

    @app.get("/healthz")
    def healthz():
        response = jsonify(
            status="ok",
            version=_VERSION,
            uptimeSeconds=int(time.monotonic() - _START),
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.post("/api/guestbook/entries")
    def create_entry():
        payload = request.get_json(silent=True, force=True)
        if not isinstance(payload, dict):
            return _error("invalid_json", 400)
        entry, errors = validate_entry(payload)
        if entry is None:
            return _error("validation_error", 400, errors)
        stored = insert_entry(
            app.config["GUESTBOOK_DB_PATH"],
            entry["author"],
            entry["message"],
            _utc_now_iso(),
        )
        return jsonify(stored), 201

    @app.get("/api/guestbook/entries")
    def get_entries():
        return jsonify(list_entries(app.config["GUESTBOOK_DB_PATH"]))

    return app


def main():
    """Console entry point: serve the API on the local development server."""
    create_app().run()

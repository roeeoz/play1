"""Payload validation for guestbook entries.

Pure functions only — no Flask, no storage — so the rules stay unit-testable
and reusable by future endpoints.
"""

from __future__ import annotations

AUTHOR_MAX = 50
MESSAGE_MAX = 300

_FIELD_LIMITS = {"author": AUTHOR_MAX, "message": MESSAGE_MAX}


def _validate_field(payload: dict, field: str, max_length: int) -> tuple[str | None, str | None]:
    """Validate one string field of *payload*.

    Returns ``(cleaned, error)`` where exactly one of the two is ``None``.
    """
    if field not in payload:
        return None, "is required"
    value = payload[field]
    if not isinstance(value, str):
        return None, "must be a string"
    cleaned = value.strip()
    if not cleaned or len(cleaned) > max_length:
        return None, f"must be between 1 and {max_length} characters"
    return cleaned, None


def validate_entry(payload: dict) -> tuple[dict[str, str] | None, dict[str, str]]:
    """Validate a create-entry payload.

    *payload* must already be a mapping; the route layer rejects anything else.
    Returns ``(entry, errors)``: on success ``entry`` holds the stripped
    ``author`` and ``message`` and ``errors`` is empty; on failure ``entry`` is
    ``None`` and ``errors`` maps each failing field name to a message.

    >>> validate_entry({"author": " Ada ", "message": "hi"})
    ({'author': 'Ada', 'message': 'hi'}, {})
    """
    cleaned: dict[str, str] = {}
    errors: dict[str, str] = {}
    for field, max_length in _FIELD_LIMITS.items():
        value, error = _validate_field(payload, field, max_length)
        if error is None:
            cleaned[field] = value
        else:
            errors[field] = error
    if errors:
        return None, errors
    return cleaned, errors

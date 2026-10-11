"""guestbook — a small JSON API for play1's guestbook entries.

Exposes two endpoints, ``POST`` and ``GET /api/guestbook/entries``, backed by a
SQLite file. See README.md for the contract and how to run the service.
"""

from guestbook.app import create_app

__all__ = ["create_app"]

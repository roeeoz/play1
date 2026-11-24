"""Read the project's ``QA_S4_MARKER`` environment value."""

from __future__ import annotations

import os

_VARIABLE = "QA_S4_MARKER"


def marker() -> str:
    """Return the value of ``QA_S4_MARKER`` from the process environment.

    The value is read on every call and returned unchanged (no trimming).
    When the variable is unset, an empty string is returned.
    """
    return os.environ.get(_VARIABLE, "")

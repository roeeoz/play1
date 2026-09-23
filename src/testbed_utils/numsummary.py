"""Console script: summarize the numbers in a file or on standard input."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from testbed_utils.numutils import mean, median, percentile

# Keep at or under 76 characters so argparse prints it on one line at 80 columns.
_DESCRIPTION = (
    "Print count, min, max, mean, median and p90 of numbers in a file or stdin."
)

_NO_NUMBERS_MSG = "no numbers found in input"


def _parse_number(token: str) -> int | float | None:
    """Return *token* as an int or finite float, or None if it is not a plain number."""
    try:
        return int(token)
    except ValueError:
        pass
    try:
        value = float(token)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def parse_numbers(text: str) -> list[int | float]:
    """Return every whitespace-separated numeric token in *text*, skipping the rest."""
    return [value for value in map(_parse_number, text.split()) if value is not None]


def is_within_cwd(path: str) -> bool:
    """True if *path*, fully resolved, is the current working directory or beneath it."""
    cwd = Path.cwd().resolve()
    resolved = Path(path).resolve()
    return resolved == cwd or resolved.is_relative_to(cwd)


def read_text(path: str | None) -> str:
    """Read the input as text: stdin when *path* is None, else a file inside the cwd."""
    if path is None:
        return sys.stdin.read()
    if not is_within_cwd(path):
        raise ValueError(f"path not allowed: '{path}' is outside the current directory")
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"Cannot open '{path}': {exc}") from exc


def format_value(value: int | float) -> str:
    """Print integral values without a decimal part; otherwise Python's default."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def summarize(numbers: list[int | float]) -> list[tuple[str, int | float]]:
    """Return the six statistics in output order."""
    return [
        ("count", len(numbers)),
        ("min", min(numbers)),
        ("max", max(numbers)),
        ("mean", mean(numbers)),
        ("median", median(numbers)),
        ("p90", percentile(numbers, 90)),
    ]


def main():
    parser = argparse.ArgumentParser(
        prog="testbed-num-summary", description=_DESCRIPTION
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Text file of whitespace-separated numbers (default: read stdin).",
    )
    args = parser.parse_args()

    try:
        numbers = parse_numbers(read_text(args.path))
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not numbers:
        print(f"Error: {_NO_NUMBERS_MSG}", file=sys.stderr)
        sys.exit(1)

    for name, value in summarize(numbers):
        print(f"{name}: {format_value(value)}")

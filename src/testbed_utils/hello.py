"""Console script: print a hello-world greeting."""

from __future__ import annotations

import argparse

# Keep at or under 76 characters so argparse prints it on one line at 80 columns.
_DESCRIPTION = "Print a hello-world greeting to standard output."


def hello_world() -> str:
    """Return the canonical hello-world greeting.

    >>> hello_world()
    'Hello, world!'
    """
    return "Hello, world!"


def main():
    parser = argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)
    parser.add_argument(
        "--name",
        default=None,
        metavar="NAME",
        help="name to greet; blank or omitted greets the world",
    )
    args = parser.parse_args()
    name = (args.name or "").strip()
    if name:
        print(f"Hello, {name}!")
    else:
        print(hello_world())

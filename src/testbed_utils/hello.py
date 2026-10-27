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
    parser.add_argument("--version", action="version", version="0.1.0")
    parser.parse_args()
    print(hello_world())

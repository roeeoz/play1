"""Console script: print a hello-world greeting."""

from __future__ import annotations

import argparse

# Keep at or under 76 characters so argparse prints it on one line at 80 columns.
_DESCRIPTION = "Print a hello-world greeting to standard output."

# Greeting word per supported --lang code; ", world!" is never translated.
_GREETING_WORDS = {"en": "Hello", "es": "Hola"}


def hello_world() -> str:
    """Return the canonical hello-world greeting.

    >>> hello_world()
    'Hello, world!'
    """
    return "Hello, world!"


def main():
    parser = argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)
    parser.add_argument(
        "--lang",
        choices=tuple(_GREETING_WORDS),
        default="en",
        help="greeting language (default: en)",
    )
    args = parser.parse_args()
    if args.lang == "en":
        print(hello_world())
    else:
        print(f"{_GREETING_WORDS[args.lang]}, world!")

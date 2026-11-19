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


# Greeting printed for each --lang choice; "en" is the default.
_GREETINGS = {
    "en": hello_world(),
    "es": "Hola, world!",
}


def main():
    parser = argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)
    parser.add_argument(
        "--lang",
        choices=list(_GREETINGS),
        default="en",
        help="greeting language (default: en)",
    )
    args = parser.parse_args()
    print(_GREETINGS[args.lang])

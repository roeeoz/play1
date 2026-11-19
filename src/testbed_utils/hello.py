"""Console script: print a greeting, by name or to the world."""

from __future__ import annotations

import argparse
import sys

# Keep at or under 76 characters so argparse prints it on one line at 80 columns.
_DESCRIPTION = "Print a greeting, by name or to the world, to standard output."


def hello_world(name: str | None = None) -> str:
    """Return the greeting for ``name``, or the hello-world greeting.

    Leading and trailing whitespace is removed and case is kept; a missing,
    empty or whitespace-only name gives the canonical greeting.

    >>> hello_world()
    'Hello, world!'
    >>> hello_world("Dana")
    'Hello, Dana!'
    >>> hello_world(" dana ")
    'Hello, dana!'
    >>> hello_world(" ")
    'Hello, world!'
    """
    name = (name or "").strip()
    if not name:
        return "Hello, world!"
    return f"Hello, {name}!"


def main():
    parser = argparse.ArgumentParser(
        prog="testbed-hello",
        description=_DESCRIPTION,
        epilog="example: testbed-hello Dana",
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="name to greet, e.g. Dana; quote a name with spaces (default: world)",
    )
    argv = sys.argv[1:]
    args = parser.parse_args(argv)
    # argparse accepts "-1" or "-" as a positional; treat any dash-led name as an
    # unknown option unless it follows the "--" separator. With one positional,
    # the name came after "--" exactly when it is all that follows the separator.
    after_separator = argv[argv.index("--") + 1 :] if "--" in argv else []
    if (
        args.name is not None
        and args.name.startswith("-")
        and after_separator != [args.name]
    ):
        parser.error(f"unrecognized arguments: {args.name}")
    print(hello_world(args.name))

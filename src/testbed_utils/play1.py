"""play1 CLI entry point."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import version as _pkg_version

_version = _pkg_version("testbed-utils")


def main() -> None:
    if "--version" in sys.argv[1:]:
        print(f"play1 {_version}")
        sys.exit(0)

    parser = argparse.ArgumentParser(
        prog="play1",
        description="play1 command-line tool.",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.parse_args()

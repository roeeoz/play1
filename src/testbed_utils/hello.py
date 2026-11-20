"""Console script: print a hello-world greeting."""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version

# Distribution name as declared in pyproject.toml ([project] name).
_DISTRIBUTION = "testbed-utils"

# Keep at or under 76 characters so argparse prints it on one line at 80 columns.
_DESCRIPTION = "Print a hello-world greeting to standard output."


def hello_world() -> str:
    """Return the canonical hello-world greeting.

    >>> hello_world()
    'Hello, world!'
    """
    return "Hello, world!"


def _package_version() -> str:
    """Return the version the installed distribution declares.

    Falls back to the package's ``__version__`` when no installed metadata is
    found (e.g. the package is imported from source without an install).
    """
    try:
        return version(_DISTRIBUTION)
    except PackageNotFoundError:
        # Imported lazily: testbed_utils/__init__.py imports this module
        # before it defines __version__.
        from testbed_utils import __version__

        return __version__


def main():
    parser = argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {_package_version()}"
    )
    parser.parse_args()
    print(hello_world())

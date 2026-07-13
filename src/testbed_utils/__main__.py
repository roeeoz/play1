"""CLI entrypoint for testbed-utils.

Run as:  python -m testbed_utils --version
         testbed-utils --version  (when installed as a console script)
"""

import sys

from testbed_utils import __version__


_USAGE = "usage: testbed-utils [--version]"


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if "--version" in argv:
        print(__version__)
        sys.exit(0)
    print(_USAGE, file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()

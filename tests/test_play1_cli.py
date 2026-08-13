import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from importlib.metadata import version as _pkg_version
from unittest.mock import patch

from testbed_utils.play1 import main


def run_main(args):
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    exit_code = 0
    with patch("sys.argv", ["play1"] + args):
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                main()
            except SystemExit as exc:
                exit_code = exc.code if exc.code is not None else 0
    return exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()


class TestPlay1Version:
    def test_version_exit_code_zero(self):
        exit_code, _, _ = run_main(["--version"])
        assert exit_code == 0

    def test_version_stdout_format(self):
        _, stdout, _ = run_main(["--version"])
        assert stdout == f"play1 {_pkg_version('testbed-utils')}\n"

    def test_version_stderr_empty(self):
        _, _, stderr = run_main(["--version"])
        assert stderr == ""

    def test_version_precedence_version_first(self):
        exit_code, stdout, _ = run_main(["--version", "--some-other-flag"])
        assert exit_code == 0
        assert stdout.startswith("play1 ")

    def test_version_precedence_version_last(self):
        exit_code, stdout, _ = run_main(["--some-other-flag", "--version"])
        assert exit_code == 0
        assert stdout.startswith("play1 ")

    def test_help_lists_version(self):
        exit_code, stdout, _ = run_main(["--help"])
        assert exit_code == 0
        assert "--version" in stdout

import io
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import pytest

from testbed_utils.hello import _DESCRIPTION, main

GREETING = "Hello, world!\n"


def run_main(args):
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    exit_code = 0
    with patch("sys.argv", ["testbed-hello"] + args):
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                main()
            except SystemExit as exc:
                exit_code = exc.code if exc.code is not None else 0
    return exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()


class TestGreeting:
    def test_prints_greeting(self):
        exit_code, stdout, stderr = run_main([])
        assert exit_code == 0
        assert stdout == GREETING
        assert stderr == ""


class TestGreetingByName:
    @pytest.mark.parametrize(
        "args, expected",
        [
            (["Dana"], "Hello, Dana!\n"),
            ([" dana "], "Hello, dana!\n"),
            (["Dana Star"], "Hello, Dana Star!\n"),
            ([""], GREETING),
            ([" "], GREETING),
            # RK2: a single bare word, rejected before, is now the name.
            (["extra"], "Hello, extra!\n"),
            (["--", "-x"], "Hello, -x!\n"),
        ],
    )
    def test_prints_greeting_for_name(self, args, expected):
        exit_code, stdout, stderr = run_main(args)
        assert exit_code == 0
        assert stdout == expected
        assert stderr == ""


class TestHelp:
    @pytest.mark.parametrize("arg", ["--help", "-h"])
    def test_help(self, arg):
        exit_code, stdout, stderr = run_main([arg])
        assert exit_code == 0
        assert stderr == ""
        assert "usage:" in stdout
        assert _DESCRIPTION in " ".join(stdout.split())
        assert "name" in stdout
        assert "Dana" in stdout
        assert "testbed-hello Dana" in stdout
        assert "Hello, " not in stdout

    def test_summary_fits_one_line(self):
        assert len(_DESCRIPTION) <= 76
        assert "\n" not in _DESCRIPTION


class TestBadOption:
    @pytest.mark.parametrize(
        "args",
        [["--bogus"], ["-x"], ["-1"], ["-"], ["-1", "--"], ["Dana", "Star"]],
    )
    def test_unrecognized_option(self, args):
        exit_code, stdout, stderr = run_main(args)
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr
        assert "error" in stderr
        assert "Hello, " not in stderr

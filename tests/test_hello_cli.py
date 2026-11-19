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


class TestHelp:
    def test_help(self):
        exit_code, stdout, stderr = run_main(["--help"])
        assert exit_code == 0
        assert stderr == ""
        assert "usage:" in stdout
        assert _DESCRIPTION in " ".join(stdout.split())
        assert "Hello, world!" not in stdout


class TestBadOption:
    @pytest.mark.parametrize("arg", ["--bogus", "-x", "extra"])
    def test_unrecognized_option(self, arg):
        exit_code, stdout, stderr = run_main([arg])
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr
        assert "error" in stderr
        assert "Hello, world!" not in stderr


class TestName:
    @pytest.mark.parametrize(
        "args, expected",
        [
            (["--name", "Alice"], "Hello, Alice!\n"),
            (["--name=Alice"], "Hello, Alice!\n"),
            (["--name", "Ada Lovelace"], "Hello, Ada Lovelace!\n"),
            (["--name", ""], "Hello, !\n"),
            (["--name", "A", "--name", "B"], "Hello, B!\n"),
        ],
    )
    def test_greets_by_name(self, args, expected):
        exit_code, stdout, stderr = run_main(args)
        assert exit_code == 0
        assert stdout == expected
        assert stderr == ""

    def test_without_name_greets_world(self):
        exit_code, stdout, stderr = run_main([])
        assert exit_code == 0
        assert stdout == GREETING
        assert stderr == ""

    def test_name_without_value_is_usage_error(self):
        exit_code, stdout, stderr = run_main(["--name"])
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr
        assert "error" in stderr

    def test_help_lists_name_option(self):
        exit_code, stdout, stderr = run_main(["--help"])
        assert exit_code == 0
        assert stderr == ""
        assert "--name NAME" in stdout
        assert "Hello, world!" not in stdout

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


class TestName:
    @pytest.mark.parametrize(
        "name, expected",
        [
            ("Alice", "Hello, Alice!\n"),
            ("alice", "Hello, alice!\n"),
            ("  Bob ", "Hello, Bob!\n"),
            (" Ada  Lee ", "Hello, Ada  Lee!\n"),
        ],
    )
    def test_greets_name(self, name, expected):
        exit_code, stdout, stderr = run_main(["--name", name])
        assert exit_code == 0
        assert stdout == expected
        assert stderr == ""

    def test_name_with_inner_space(self):
        exit_code, stdout, stderr = run_main(["--name", "Ada Lovelace"])
        assert exit_code == 0
        assert stdout == "Hello, Ada Lovelace!\n"
        assert stderr == ""

    @pytest.mark.parametrize("name", ["", " ", "   "])
    def test_blank_name_falls_back(self, name):
        exit_code, stdout, stderr = run_main(["--name", name])
        assert exit_code == 0
        assert stdout == GREETING
        assert stderr == ""

    def test_missing_value(self):
        exit_code, stdout, stderr = run_main(["--name"])
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr
        assert "error" in stderr
        assert "Hello," not in stderr


class TestHelp:
    def test_help(self):
        with patch.dict("os.environ", {"COLUMNS": "80"}):
            exit_code, stdout, stderr = run_main(["--help"])
        assert exit_code == 0
        assert stderr == ""
        assert "usage:" in stdout
        assert _DESCRIPTION in [line.strip() for line in stdout.splitlines()]
        assert "--name" in stdout
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

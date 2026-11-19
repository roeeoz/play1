import io
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import pytest

from testbed_utils.hello import _DESCRIPTION, main

GREETING = "Hello, world!\n"
GREETING_ES = "Hola, world!\n"


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


class TestLang:
    @pytest.mark.parametrize("args", [["--lang", "en"], ["--lang=en"]])
    def test_english(self, args):
        exit_code, stdout, stderr = run_main(args)
        assert exit_code == 0
        assert stdout == GREETING
        assert stderr == ""

    @pytest.mark.parametrize("args", [["--lang", "es"], ["--lang=es"]])
    def test_spanish(self, args):
        exit_code, stdout, stderr = run_main(args)
        assert exit_code == 0
        assert stdout == GREETING_ES
        assert stderr == ""

    @pytest.mark.parametrize("value", ["fr", "ES", ""])
    def test_invalid_value(self, value):
        exit_code, stdout, stderr = run_main(["--lang", value])
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr
        assert "error" in stderr
        assert "en" in stderr
        assert "es" in stderr

    def test_missing_value(self):
        exit_code, stdout, stderr = run_main(["--lang"])
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr
        assert "error" in stderr

    def test_help_lists_lang(self):
        exit_code, stdout, stderr = run_main(["--help"])
        assert exit_code == 0
        assert stderr == ""
        assert "--lang" in stdout
        assert "{en,es}" in stdout
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

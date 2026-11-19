import io
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import pytest

from testbed_utils.hello import _DESCRIPTION, hello_world, main

GREETING = "Hello, world!\n"
SPANISH_GREETING = "Hola, world!\n"


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

    @pytest.mark.parametrize("args", [["--lang", "en"], ["--lang=en"]])
    def test_english_lang(self, args):
        exit_code, stdout, stderr = run_main(args)
        assert exit_code == 0
        assert stdout == GREETING
        assert stdout == hello_world() + "\n"
        assert stderr == ""

    @pytest.mark.parametrize("args", [["--lang", "es"], ["--lang=es"]])
    def test_spanish_lang(self, args):
        exit_code, stdout, stderr = run_main(args)
        assert exit_code == 0
        assert stdout == SPANISH_GREETING
        assert stdout == "Hola, world!\n"
        assert stderr == ""


class TestBadLang:
    @pytest.mark.parametrize(
        "args", [["--lang", "fr"], ["--lang", "ES"], ["--lang"]]
    )
    def test_rejected(self, args):
        exit_code, stdout, stderr = run_main(args)
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr
        assert "error" in stderr
        for greeting in ("Hello, world!", "Hola, world!"):
            assert greeting not in stdout
            assert greeting not in stderr


class TestHelp:
    def test_help(self):
        exit_code, stdout, stderr = run_main(["--help"])
        assert exit_code == 0
        assert stderr == ""
        assert "usage:" in stdout
        assert _DESCRIPTION in " ".join(stdout.split())
        assert "Hello, world!" not in stdout
        assert "Hola, world!" not in stdout
        assert "--lang" in stdout
        assert "{en,es}" in stdout


class TestBadOption:
    @pytest.mark.parametrize("arg", ["--bogus", "-x", "extra"])
    def test_unrecognized_option(self, arg):
        exit_code, stdout, stderr = run_main([arg])
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr
        assert "error" in stderr
        assert "Hello, world!" not in stderr
        assert "Hola, world!" not in stderr

import io
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as metadata_version
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import pytest

import testbed_utils

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
        assert "--version" in stdout


class TestBadOption:
    @pytest.mark.parametrize("arg", ["--bogus", "-x", "extra", "-V", "--no-such-option"])
    def test_unrecognized_option(self, arg):
        exit_code, stdout, stderr = run_main([arg])
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr
        assert "error" in stderr
        assert "Hello, world!" not in stderr


class TestVersion:
    def test_prints_version_line(self):
        exit_code, stdout, stderr = run_main(["--version"])
        assert exit_code == 0
        assert stdout == "testbed-hello 0.1.0\n"
        assert stderr == ""

    def test_no_greeting(self):
        _, stdout, stderr = run_main(["--version"])
        assert "Hello, world!" not in stdout
        assert "Hello, world!" not in stderr

    def test_follows_installed_metadata(self):
        with patch("testbed_utils.hello.version", return_value="9.9.9"):
            exit_code, stdout, stderr = run_main(["--version"])
        assert exit_code == 0
        assert stdout == "testbed-hello 9.9.9\n"
        assert stderr == ""

    def test_package_version_matches_metadata(self):
        assert testbed_utils.__version__ == metadata_version("testbed-utils")

    def test_missing_metadata_falls_back_to_package_version(self):
        missing = PackageNotFoundError("testbed-utils")
        with patch("testbed_utils.hello.version", side_effect=missing):
            exit_code, stdout, stderr = run_main(["--version"])
            assert exit_code == 0
            assert stdout == f"testbed-hello {testbed_utils.__version__}\n"
            assert stderr == ""

            exit_code, stdout, stderr = run_main([])
            assert exit_code == 0
            assert stdout == GREETING

            exit_code, stdout, _ = run_main(["--help"])
            assert exit_code == 0
            assert "--version" in stdout

    @pytest.mark.parametrize(
        "args",
        [["--version", "extra"], ["--bogus", "--version"], ["--version", "--help"]],
    )
    def test_combined_arguments(self, args):
        exit_code, stdout, stderr = run_main(args)
        assert exit_code == 0
        assert stdout == "testbed-hello 0.1.0\n"
        assert stderr == ""

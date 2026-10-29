import io
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import pytest

from testbed_utils.dateutils import _DESCRIPTION, main


def run_main(args):
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    exit_code = 0
    with patch("sys.argv", ["testbed-date-range"] + args):
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                main()
            except SystemExit as exc:
                exit_code = exc.code if exc.code is not None else 0
    return exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()


class TestDayCount:
    def test_happy_path(self):
        exit_code, stdout, stderr = run_main(["2024-01-01", "2024-01-10"])
        assert exit_code == 0
        assert stdout == "9\n"
        assert stderr == ""

    def test_reversed_order(self):
        exit_code, stdout, _ = run_main(["2024-01-10", "2024-01-01"])
        assert exit_code == 0
        assert stdout == "9\n"

    def test_identical_dates(self):
        exit_code, stdout, stderr = run_main(["2024-06-15", "2024-06-15"])
        assert exit_code == 0
        assert stdout == "0\n"
        assert stderr == ""

    def test_trailing_z(self):
        exit_code, stdout, _ = run_main(["2024-01-01", "2024-01-10Z"])
        assert exit_code == 0
        assert stdout == "9\n"


class TestHelp:
    def test_help(self):
        exit_code, stdout, stderr = run_main(["--help"])
        assert exit_code == 0
        assert stderr == ""
        assert "usage:" in stdout
        assert _DESCRIPTION in " ".join(stdout.split())


class TestInvalidInput:
    def test_bad_date(self):
        exit_code, stdout, stderr = run_main(["not-a-date", "2024-01-01"])
        assert exit_code == 1
        assert stdout == ""
        assert "Error:" in stderr

    def test_missing_args(self):
        exit_code, stdout, stderr = run_main([])
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr

    @pytest.mark.parametrize("arg", ["--bogus", "-x"])
    def test_unrecognized_option(self, arg):
        exit_code, stdout, stderr = run_main([arg])
        assert exit_code == 2
        assert stdout == ""
        assert "usage:" in stderr

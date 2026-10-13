import io
import os
import pathlib
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import pytest

from testbed_utils.numsummary import _DESCRIPTION, main

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

FILE_SUMMARY = "count: 5\nmin: 1\nmax: 5\nmean: 3\nmedian: 3\np90: 4.6\n"
STDIN_SUMMARY = "count: 3\nmin: 10\nmax: 30\nmean: 20\nmedian: 20\np90: 28\n"
SINGLE_SUMMARY = "count: 1\nmin: 42\nmax: 42\nmean: 42\nmedian: 42\np90: 42\n"


def run_main(args, stdin_text=""):
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    exit_code = 0
    with patch("sys.argv", ["testbed-num-summary"] + args), patch(
        "sys.stdin", io.StringIO(stdin_text)
    ):
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                main()
            except SystemExit as exc:
                exit_code = exc.code if exc.code is not None else 0
    return exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()


def assert_one_line(text):
    assert text.endswith("\n")
    assert text.count("\n") == 1


class TestFileInput:
    def test_summary_from_file(self, monkeypatch):
        monkeypatch.chdir(FIXTURES)
        exit_code, stdout, stderr = run_main(["numbers.txt"])
        assert stdout == FILE_SUMMARY
        assert stderr == ""
        assert exit_code == 0

    def test_single_number(self, monkeypatch):
        monkeypatch.chdir(FIXTURES)
        exit_code, stdout, stderr = run_main(["single.txt"])
        assert stdout == SINGLE_SUMMARY
        assert stderr == ""
        assert exit_code == 0

    def test_empty_file(self, monkeypatch):
        monkeypatch.chdir(FIXTURES)
        exit_code, stdout, stderr = run_main(["empty.txt"])
        assert exit_code == 1
        assert stdout == ""
        assert_one_line(stderr)
        assert "no numbers found" in stderr

    def test_only_junk_tokens(self, monkeypatch, tmp_path):
        (tmp_path / "junk.txt").write_text("nan inf -inf abc 0x10\n")
        monkeypatch.chdir(tmp_path)
        exit_code, stdout, stderr = run_main(["junk.txt"])
        assert exit_code == 1
        assert stdout == ""
        assert_one_line(stderr)
        assert "no numbers found" in stderr

    def test_missing_file(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        exit_code, stdout, stderr = run_main(["missing.txt"])
        assert exit_code == 1
        assert stdout == ""
        assert_one_line(stderr)
        assert stderr.startswith("Error: Cannot open")

    def test_directory_path(self, monkeypatch, tmp_path):
        (tmp_path / "sub").mkdir()
        monkeypatch.chdir(tmp_path)
        exit_code, stdout, stderr = run_main(["sub"])
        assert exit_code == 1
        assert stdout == ""
        assert_one_line(stderr)
        assert stderr.startswith("Error:")


class TestStdinInput:
    def test_summary_from_stdin(self):
        exit_code, stdout, stderr = run_main([], stdin_text="10\n20\n30\n")
        assert stdout == STDIN_SUMMARY
        assert stderr == ""
        assert exit_code == 0

    def test_empty_stdin(self):
        exit_code, stdout, stderr = run_main([], stdin_text="")
        assert exit_code == 1
        assert stdout == ""
        assert_one_line(stderr)
        assert "no numbers found" in stderr

    def test_mixed_tokens_skipped(self):
        exit_code, stdout, _ = run_main([], stdin_text="1 x 2\n")
        assert exit_code == 0
        assert "count: 2\n" in stdout
        assert "mean: 1.5\n" in stdout

    def test_integral_float_collapses(self):
        exit_code, stdout, _ = run_main([], stdin_text="1.5 2.5")
        assert exit_code == 0
        assert "mean: 2\n" in stdout


class TestPathSafety:
    def test_dotdot_inside_cwd_accepted(self, monkeypatch, tmp_path):
        (tmp_path / "numbers.txt").write_text("1 2 3 4 5\n")
        (tmp_path / "sub").mkdir()
        monkeypatch.chdir(tmp_path)
        exit_code, stdout, stderr = run_main([os.path.join("sub", "..", "numbers.txt")])
        assert stdout == FILE_SUMMARY
        assert stderr == ""
        assert exit_code == 0

    @pytest.mark.parametrize(
        "path",
        [
            os.path.join("..", "x.txt"),
            os.path.join("sub", "..", "..", "x.txt"),
            "/etc/passwd",
        ],
    )
    def test_escaping_path_rejected(self, monkeypatch, tmp_path, path):
        monkeypatch.chdir(tmp_path)
        exit_code, stdout, stderr = run_main([path])
        assert exit_code == 1
        assert stdout == ""
        assert_one_line(stderr)
        assert "not allowed" in stderr
        assert "no numbers" not in stderr

    def test_escaping_symlink_rejected(self, monkeypatch, tmp_path, tmp_path_factory):
        outside = tmp_path_factory.mktemp("outside") / "secret.txt"
        outside.write_text("1 2 3\n")
        os.symlink(outside, tmp_path / "link")
        monkeypatch.chdir(tmp_path)
        exit_code, stdout, stderr = run_main(["link"])
        assert exit_code == 1
        assert stdout == ""
        assert_one_line(stderr)
        assert "not allowed" in stderr


class TestHelp:
    def test_help(self):
        exit_code, stdout, stderr = run_main(["--help"])
        assert exit_code == 0
        assert stderr == ""
        assert "usage:" in stdout
        assert _DESCRIPTION in " ".join(stdout.split())

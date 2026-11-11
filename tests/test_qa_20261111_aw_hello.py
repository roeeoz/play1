import os
import pathlib
import stat
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "qa" / "20261111-aw" / "hello.sh"
EXPECTED_STDOUT = "hello aw\n"


def run_script(args=(), cwd=None):
    result = subprocess.run(
        [str(SCRIPT), *args], capture_output=True, text=True, timeout=10, cwd=cwd
    )
    return result.returncode, result.stdout, result.stderr


class TestNormalRun:
    def test_prints_hello_aw(self):
        exit_code, stdout, stderr = run_script(cwd=REPO_ROOT)
        assert exit_code == 0
        assert stdout == EXPECTED_STDOUT
        assert stderr == ""


class TestRunFromAnotherDirectory:
    def test_prints_hello_aw_from_tmp_path(self, tmp_path):
        exit_code, stdout, stderr = run_script(cwd=tmp_path)
        assert exit_code == 0
        assert stdout == EXPECTED_STDOUT
        assert stderr == ""


class TestIgnoresArguments:
    def test_extra_argument_does_not_change_output(self):
        exit_code, stdout, stderr = run_script(args=("--help",), cwd=REPO_ROOT)
        assert exit_code == 0
        assert stdout == EXPECTED_STDOUT
        assert stderr == ""


class TestScriptShape:
    def test_shebang(self):
        assert SCRIPT.read_bytes().startswith(b"#!/bin/sh\n")

    def test_executable(self):
        assert os.stat(SCRIPT).st_mode & stat.S_IXUSR

    def test_lf_line_endings(self):
        assert b"\r" not in SCRIPT.read_bytes()

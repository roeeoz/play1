import os
import pathlib
import stat
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "qa" / "20261109-s1" / "a.sh"
S3_A_SCRIPT = REPO_ROOT / "qa" / "s3-a.sh"


def run_script(script, cwd=None):
    result = subprocess.run(
        [str(script)], capture_output=True, text=True, timeout=10, cwd=cwd
    )
    return result.returncode, result.stdout, result.stderr


class TestNormalRun:
    def test_prints_a(self):
        exit_code, stdout, stderr = run_script(SCRIPT, cwd=REPO_ROOT)
        assert exit_code == 0
        assert stdout == "A\n"
        assert stderr == ""


class TestRunFromAnotherDirectory:
    def test_prints_a_from_tmp_path(self, tmp_path):
        exit_code, stdout, stderr = run_script(SCRIPT, cwd=tmp_path)
        assert exit_code == 0
        assert stdout == "A\n"
        assert stderr == ""


class TestScriptShape:
    def test_shebang(self):
        assert SCRIPT.read_bytes().startswith(b"#!/bin/sh\n")

    def test_executable(self):
        assert os.stat(SCRIPT).st_mode & stat.S_IXUSR

    def test_lf_line_endings(self):
        assert b"\r" not in SCRIPT.read_bytes()


class TestExistingS3AScriptUnchanged:
    def test_s3_a_still_prints_a(self):
        exit_code, stdout, stderr = run_script(S3_A_SCRIPT)
        assert exit_code == 0
        assert stdout == "A\n"
        assert stderr == ""

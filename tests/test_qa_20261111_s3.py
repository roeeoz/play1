import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "src" / "qa_20261111_s3.py"


def run_script(cwd):
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr


class TestNormalRun:
    def test_prints_hello_s3(self):
        exit_code, stdout, stderr = run_script(cwd=REPO_ROOT)
        assert exit_code == 0
        assert stdout == "hello s3\n"
        assert stderr == ""


class TestRunFromAnotherDirectory:
    def test_prints_hello_s3_from_tmp_path(self, tmp_path):
        exit_code, stdout, stderr = run_script(cwd=tmp_path)
        assert exit_code == 0
        assert stdout == "hello s3\n"
        assert stderr == ""

import os
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "hello-world" / "hello.sh"
EXPECTED_STDOUT = b"Hello, World!!\n"


def run_script(cwd=REPO_ROOT):
    # Executed directly, without a "bash" prefix, so the shebang and exec bit are exercised.
    result = subprocess.run([str(SCRIPT)], capture_output=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr


class TestExecution:
    def test_prints_greeting_from_repo_root(self):
        exit_code, stdout, stderr = run_script()
        assert exit_code == 0
        assert stdout == EXPECTED_STDOUT
        assert stderr == b""

    def test_prints_greeting_from_other_directory(self, tmp_path):
        exit_code, stdout, stderr = run_script(cwd=tmp_path)
        assert exit_code == 0
        assert stdout == EXPECTED_STDOUT
        assert stderr == b""


class TestFolderIsolation:
    def test_folder_holds_only_hello_sh(self):
        assert sorted(os.listdir(SCRIPT.parent)) == ["hello.sh"]


class TestShebang:
    def test_first_line_is_bash_shebang(self):
        with SCRIPT.open("rb") as f:
            assert f.readline() == b"#!/bin/bash\n"

    def test_script_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)


class TestOutputExactness:
    def test_captured_value_is_exact(self):
        _, stdout, _ = run_script()
        text = stdout.decode("ascii")
        # $(...) strips trailing newlines only.
        assert text.rstrip("\n") == "Hello, World!!"
        assert stdout.count(b"!") == 2
        assert stdout.count(b"\n") == 1
        assert b"\r" not in stdout

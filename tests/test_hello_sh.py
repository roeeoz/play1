import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FOLDER = REPO_ROOT / "hello-world"
SCRIPT = FOLDER / "hello.sh"
EXPECTED = b"hello world\n"


def run_script(cwd):
    # Run the script directly (no "bash" prefix) so the shebang and exec bit are exercised.
    return subprocess.run([str(SCRIPT)], capture_output=True, cwd=cwd, check=False)


class TestHelloScript:
    def test_prints_exact_output_from_repo_root(self):
        result = run_script(REPO_ROOT)
        assert result.returncode == 0
        assert result.stdout == EXPECTED
        assert result.stderr == b""

    def test_same_output_from_other_directory(self, tmp_path):
        first = run_script(tmp_path)
        second = run_script(tmp_path)
        assert first.returncode == 0
        assert first.stdout == EXPECTED
        assert first.stderr == b""
        assert second.stdout == first.stdout

    def test_first_line_is_bash_shebang(self):
        assert SCRIPT.read_bytes().split(b"\n", 1)[0] == b"#!/bin/bash"

    def test_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_folder_contains_only_script(self):
        assert sorted(os.listdir(FOLDER)) == ["hello.sh"]

    def test_file_is_plain_ascii_with_lf_endings(self):
        content = SCRIPT.read_bytes()
        assert not content.startswith(b"\xef\xbb\xbf")
        assert b"\r" not in content
        content.decode("ascii")
        for line in content.split(b"\n"):
            assert not line.endswith((b" ", b"\t"))

import os
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "hello-world" / "hello.sh"


class TestHelloShExecution:
    def test_prints_hello_world(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert result.stdout == "hello world\n"

    def test_no_stderr(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        assert result.stderr == ""

    def test_exact_output_no_extra_whitespace(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        assert result.stdout.strip() == "hello world"
        assert result.stdout == "hello world\n"


class TestHelloShStructure:
    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

    def test_executable_permission(self):
        mode = SCRIPT.stat().st_mode
        assert mode & stat.S_IXUSR

    def test_folder_contains_only_hello_sh(self):
        folder = SCRIPT.parent
        contents = [f.name for f in folder.iterdir() if not f.name.startswith(".")]
        assert contents == ["hello.sh"]

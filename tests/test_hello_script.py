import os
import stat
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"


class TestHelloScript:
    def test_prints_hello_world(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert result.stdout == "hello world\n"

    def test_no_stderr_output(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        assert result.stderr == ""

    def test_executable_permission(self):
        mode = os.stat(SCRIPT).st_mode
        assert mode & stat.S_IXUSR

    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"


class TestHelloWorldFolder:
    def test_contains_only_hello_sh(self):
        folder = SCRIPT.parent
        contents = list(folder.iterdir())
        assert len(contents) == 1
        assert contents[0].name == "hello.sh"

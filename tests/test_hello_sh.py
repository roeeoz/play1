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
        assert result.stderr == ""

    def test_exact_output_no_extra_whitespace(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        assert result.stdout.strip() == "hello world"
        assert result.stdout.count("\n") == 1

    def test_executable_permission(self):
        import os

        assert os.access(SCRIPT, os.X_OK)

    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

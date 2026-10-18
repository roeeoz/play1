import os
import stat
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"


class TestHelloSh:
    def test_prints_hello_world(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

    def test_executable_permission(self):
        mode = SCRIPT.stat().st_mode
        assert mode & stat.S_IXUSR

    def test_folder_contains_only_hello_sh(self):
        contents = os.listdir(SCRIPT.parent)
        assert contents == ["hello.sh"]

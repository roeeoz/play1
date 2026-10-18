import pathlib
import subprocess

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"


class TestHelloSh:
    def test_prints_hello_world(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_executable_permissions(self):
        import os
        assert os.access(SCRIPT, os.X_OK)

    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

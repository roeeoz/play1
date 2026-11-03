import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "hello-world", "hello.sh")


class TestHelloSh:
    def test_prints_hello_world(self):
        result = subprocess.run([SCRIPT], capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_executable_permission(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_shebang_line(self):
        with open(SCRIPT) as f:
            first_line = f.readline()
        assert first_line.rstrip("\n") == "#!/bin/bash"

    def test_folder_contains_only_hello_sh(self):
        folder = os.path.join(REPO_ROOT, "hello-world")
        assert os.listdir(folder) == ["hello.sh"]

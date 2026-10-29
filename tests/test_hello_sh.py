import os
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).parent.parent
SCRIPT = REPO_ROOT / "hello-world" / "hello.sh"
HELLO_DIR = REPO_ROOT / "hello-world"


class TestHelloScript:
    def test_prints_hello_world(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.stdout == "hello world\n"

    def test_exit_code_zero(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0

    def test_no_stderr(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.stderr == ""

    def test_exact_output_no_extra_lines(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.stdout.strip() == "hello world"
        assert result.stdout.count("\n") == 1


class TestHelloShellSetup:
    def test_folder_exists(self):
        assert HELLO_DIR.is_dir()

    def test_folder_contains_only_hello_sh(self):
        contents = list(HELLO_DIR.iterdir())
        assert len(contents) == 1
        assert contents[0].name == "hello.sh"

    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

    def test_executable_permission(self):
        assert os.access(SCRIPT, os.X_OK)

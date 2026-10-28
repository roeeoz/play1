import pathlib
import subprocess

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"


class TestHelloScript:
    def test_prints_hello_world(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_executable_permission(self):
        import os

        assert os.access(SCRIPT, os.X_OK)

    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

    def test_exact_output_no_extra_whitespace(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.stdout.strip() == "hello world"
        lines = result.stdout.strip().splitlines()
        assert len(lines) == 1

    def test_folder_contains_only_hello_sh(self):
        folder = SCRIPT.parent
        contents = list(folder.iterdir())
        assert len(contents) == 1
        assert contents[0].name == "hello.sh"

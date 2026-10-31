import os
import subprocess
import pathlib


SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"


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

    def test_exact_output_no_extra_whitespace(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        assert result.stdout.strip() == "hello world"
        assert result.stdout == "hello world\n"

    def test_executable_permission(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_shebang_line(self):
        with open(SCRIPT) as f:
            first_line = f.readline()
        assert first_line.strip() == "#!/bin/bash"

    def test_folder_contains_only_hello_sh(self):
        folder = SCRIPT.parent
        contents = list(folder.iterdir())
        assert len(contents) == 1
        assert contents[0].name == "hello.sh"

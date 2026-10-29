import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"


class TestHelloSh:
    def test_script_exists(self):
        assert SCRIPT.is_file()

    def test_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

    def test_prints_hello_world(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_output_exactness(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        output = result.stdout.rstrip("\n")
        assert output == "hello world"

    def test_folder_contains_only_hello_sh(self):
        folder = SCRIPT.parent
        contents = list(folder.iterdir())
        assert len(contents) == 1
        assert contents[0].name == "hello.sh"

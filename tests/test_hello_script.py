import os
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "hello-world" / "hello.sh"


class TestHelloScript:
    def test_prints_hello_world(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_executable_permission(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

    def test_folder_contains_only_hello_sh(self):
        folder = SCRIPT.parent
        contents = [f.name for f in folder.iterdir() if not f.name.startswith(".")]
        assert contents == ["hello.sh"]

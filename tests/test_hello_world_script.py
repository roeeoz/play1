import os
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).parent.parent
SCRIPT_DIR = REPO_ROOT / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def run_script():
    return subprocess.run(
        ["./hello-world/hello.sh"], cwd=REPO_ROOT, capture_output=True, text=True
    )


class TestFolder:
    def test_only_file_is_hello_sh(self):
        assert sorted(p.name for p in SCRIPT_DIR.iterdir()) == ["hello.sh"]


class TestScript:
    def test_shebang_is_first_line(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_direct_execution_prints_hello_world(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_output_is_exactly_one_line_without_padding(self):
        lines = run_script().stdout.splitlines()
        assert lines == ["hello world"]

import os
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT_DIR = REPO_ROOT / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def run_script():
    return subprocess.run(
        ["./hello-world/hello.sh"], cwd=REPO_ROOT, capture_output=True, text=True
    )


class TestHelloWorldScript:
    def test_folder_contains_only_script(self):
        assert SCRIPT_DIR.is_dir()
        assert [p.name for p in SCRIPT_DIR.iterdir()] == ["hello.sh"]

    def test_shebang_is_bash(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_script_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_direct_execution_exits_zero(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stderr == ""

    def test_output_is_exactly_hello_world(self):
        result = run_script()
        assert result.stdout == "hello world\n"
        assert result.stdout.splitlines() == ["hello world"]

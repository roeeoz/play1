import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FOLDER = REPO_ROOT / "hello-world"
SCRIPT = FOLDER / "hello.sh"


def run_script():
    return subprocess.run(
        ["./hello-world/hello.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class TestHelloWorldScript:
    def test_folder_exists_at_repo_root(self):
        assert FOLDER.is_dir()

    def test_folder_contains_only_hello_sh(self):
        assert sorted(p.name for p in FOLDER.iterdir()) == ["hello.sh"]

    def test_first_line_is_bash_shebang(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_direct_execution_prints_hello_world_and_exits_zero(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stderr == ""

    def test_output_is_exactly_hello_world(self):
        result = run_script()
        assert result.stdout == "hello world\n"
        assert result.stdout.splitlines() == ["hello world"]

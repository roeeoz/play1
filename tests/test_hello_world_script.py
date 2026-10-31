import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = REPO_ROOT / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def _run_directly():
    return subprocess.run(
        ["./hello-world/hello.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class TestHelloWorldScript:
    def test_folder_exists_at_repo_root(self):
        assert SCRIPT_DIR.is_dir()

    def test_folder_contains_only_hello_sh(self):
        assert sorted(p.name for p in SCRIPT_DIR.iterdir()) == ["hello.sh"]

    def test_first_line_is_bash_shebang(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_direct_execution_exits_zero(self):
        assert _run_directly().returncode == 0

    def test_prints_exactly_hello_world(self):
        result = _run_directly()
        # echo's single line terminator is the only byte beyond the text
        assert result.stdout == "hello world\n"

    def test_writes_nothing_to_stderr(self):
        assert _run_directly().stderr == ""

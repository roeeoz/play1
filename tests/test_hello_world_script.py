import os
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = REPO_ROOT / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def run_script():
    # Executed directly (no `bash` prefix) so the shebang is what picks the shell.
    return subprocess.run(
        ["./hello-world/hello.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestHelloWorldFolder:
    def test_folder_exists_at_repo_root(self):
        assert SCRIPT_DIR.is_dir()

    def test_folder_contains_only_hello_sh(self):
        assert sorted(p.name for p in SCRIPT_DIR.iterdir()) == ["hello.sh"]


class TestHelloScript:
    def test_first_line_is_bash_shebang(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_is_executable(self):
        assert SCRIPT.stat().st_mode & stat.S_IXUSR
        assert os.access(SCRIPT, os.X_OK)

    def test_runs_directly_and_exits_zero(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stderr == ""

    def test_prints_exactly_hello_world(self):
        result = run_script()
        assert result.stdout == "hello world\n"
        assert result.stdout.splitlines() == ["hello world"]

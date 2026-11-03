import os
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = REPO_ROOT / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def run_script():
    # Invoke the script directly (no explicit `bash`) so the shebang is exercised.
    return subprocess.run(
        ["./hello-world/hello.sh"], cwd=REPO_ROOT, capture_output=True, text=True
    )


class TestFolder:
    def test_folder_exists_at_repo_root(self):
        assert SCRIPT_DIR.is_dir()

    def test_only_file_is_hello_sh(self):
        assert sorted(p.name for p in SCRIPT_DIR.iterdir()) == ["hello.sh"]


class TestScriptFile:
    def test_shebang(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_executable(self):
        assert SCRIPT.stat().st_mode & stat.S_IXUSR
        assert os.access(SCRIPT, os.X_OK)


class TestExecution:
    def test_prints_hello_world_and_exits_zero(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stderr == ""

    def test_output_is_exactly_hello_world(self):
        result = run_script()
        # A single line terminated by newline: no surrounding whitespace, no extra lines.
        assert result.stdout == "hello world\n"
        assert result.stdout.splitlines() == ["hello world"]

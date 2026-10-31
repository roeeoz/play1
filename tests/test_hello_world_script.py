import os
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def run_script():
    # Invoke the script directly (no `bash` prefix) so the shebang is exercised.
    return subprocess.run(
        ["./hello-world/hello.sh"],
        cwd=SCRIPT_DIR.parent,
        capture_output=True,
        text=True,
        check=False,
    )


class TestHelloWorldFolder:
    def test_folder_contains_only_hello_sh(self):
        assert SCRIPT_DIR.is_dir()
        assert sorted(p.name for p in SCRIPT_DIR.iterdir()) == ["hello.sh"]


class TestHelloWorldScript:
    def test_starts_with_bash_shebang(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_runs_directly_and_exits_zero(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stderr == ""

    def test_prints_exactly_hello_world(self):
        result = run_script()
        assert result.stdout == "hello world\n"
        assert result.stdout.splitlines() == ["hello world"]

import os
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FOLDER = REPO_ROOT / "hello-world"
SCRIPT = FOLDER / "hello.sh"


def run_script():
    # Invoke the script directly (no "bash" prefix) so the shebang is exercised.
    return subprocess.run(
        ["./hello-world/hello.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class TestHelloWorldScript:
    def test_folder_contains_only_hello_sh(self):
        assert FOLDER.is_dir()
        assert sorted(p.name for p in FOLDER.iterdir()) == ["hello.sh"]

    def test_starts_with_bash_shebang(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

    def test_is_executable(self):
        mode = SCRIPT.stat().st_mode
        assert mode & stat.S_IXUSR
        assert os.access(SCRIPT, os.X_OK)

    def test_direct_execution_prints_exactly_hello_world(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stdout.splitlines() == ["hello world"]
        assert result.stderr == ""

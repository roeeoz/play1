import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = REPO_ROOT / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def run_script():
    return subprocess.run(
        ["./hello-world/hello.sh"], cwd=REPO_ROOT, capture_output=True
    )


class TestFolder:
    def test_folder_exists_at_repo_root(self):
        assert SCRIPT_DIR.is_dir()

    def test_folder_contains_only_hello_sh(self):
        assert sorted(p.name for p in SCRIPT_DIR.iterdir()) == ["hello.sh"]


class TestScript:
    def test_starts_with_bash_shebang(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_direct_execution_prints_hello_world(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stdout == b"hello world"
        assert result.stderr == b""

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


class TestFolder:
    def test_folder_at_repo_root(self):
        assert FOLDER.is_dir()

    def test_only_file_is_hello_sh(self):
        assert sorted(p.name for p in FOLDER.iterdir()) == ["hello.sh"]


class TestScript:
    def test_shebang(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_runs_directly_and_prints_hello_world(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_output_is_single_exact_line(self):
        lines = run_script().stdout.splitlines()
        assert lines == ["hello world"]
        assert lines[0] == lines[0].strip()

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = REPO_ROOT / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def run_script():
    return subprocess.run(
        ["./hello-world/hello.sh"], cwd=REPO_ROOT, capture_output=True, text=True
    )


def test_folder_contains_only_script():
    assert SCRIPT_DIR.is_dir()
    assert sorted(p.name for p in SCRIPT_DIR.iterdir()) == ["hello.sh"]


def test_shebang_is_first_line():
    assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"


def test_script_is_executable():
    assert os.access(SCRIPT, os.X_OK)


def test_direct_execution_prints_hello_world():
    result = run_script()
    assert result.returncode == 0
    assert result.stdout == "hello world\n"
    assert result.stderr == ""


def test_output_is_exact_single_line():
    lines = run_script().stdout.splitlines()
    assert lines == ["hello world"]

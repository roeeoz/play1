import os
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def run_script():
    # Invoke the file directly (no explicit `bash`) so the shebang is exercised.
    return subprocess.run([str(SCRIPT)], capture_output=True, text=True, timeout=10)


class TestFolder:
    def test_only_file_is_hello_sh(self):
        assert SCRIPT_DIR.is_dir()
        assert sorted(p.name for p in SCRIPT_DIR.iterdir()) == ["hello.sh"]


class TestScriptFile:
    def test_shebang_is_first_line(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)


class TestExecution:
    def test_prints_hello_world_and_exits_zero(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stderr == ""
        assert result.stdout.strip() == "hello world"

    def test_output_is_exact_single_line(self):
        result = run_script()
        assert result.stdout == "hello world\n"
        assert result.stdout.splitlines() == ["hello world"]

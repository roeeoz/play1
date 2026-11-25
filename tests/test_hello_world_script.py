import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"

EXPECTED = "Hello, World!!\n"


def test_runs_directly_and_prints_greeting():
    result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout == EXPECTED
    assert result.stderr == ""


def test_has_bash_shebang():
    assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"


def test_is_executable():
    assert os.access(SCRIPT, os.X_OK)


def test_folder_contains_only_script():
    assert sorted(os.listdir(SCRIPT.parent)) == ["hello.sh"]

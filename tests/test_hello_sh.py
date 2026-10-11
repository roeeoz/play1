import pathlib
import subprocess

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "hello-world" / "hello.sh"


class TestHelloSh:
    def test_prints_hello_world(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.stdout == "Hello, World!\n"

    def test_exit_code_zero(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0

    def test_stderr_is_empty(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.stderr == ""

    def test_executable_permission(self):
        import os
        assert os.access(SCRIPT, os.X_OK)

    def test_valid_bash_shebang(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line in ("#!/bin/bash", "#!/usr/bin/env bash")

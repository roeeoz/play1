import os
import subprocess

SCRIPT = os.path.join(os.path.dirname(__file__), os.pardir, "hello-world", "hello.sh")


class TestHelloScript:
    def test_prints_hello_world(self):
        result = subprocess.run([SCRIPT], capture_output=True, text=True)
        assert result.stdout == "hello world\n"

    def test_exits_with_code_zero(self):
        result = subprocess.run([SCRIPT], capture_output=True, text=True)
        assert result.returncode == 0

    def test_no_stderr_output(self):
        result = subprocess.run([SCRIPT], capture_output=True, text=True)
        assert result.stderr == ""

    def test_exact_output_no_extra_lines(self):
        result = subprocess.run([SCRIPT], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        assert len(lines) == 1
        assert lines[0] == "hello world"

    def test_executable_without_explicit_bash(self):
        result = subprocess.run([SCRIPT], capture_output=True, text=True)
        assert result.returncode == 0

    def test_shebang_line(self):
        with open(SCRIPT) as f:
            first_line = f.readline().rstrip("\n")
        assert first_line == "#!/bin/bash"

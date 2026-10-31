import os
import subprocess

SCRIPT = os.path.join(os.path.dirname(__file__), os.pardir, "hello-world", "hello.sh")


class TestHelloScript:
    def test_prints_hello_world(self):
        result = subprocess.run(
            [SCRIPT], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert result.stdout == "hello world\n"

    def test_no_stderr(self):
        result = subprocess.run(
            [SCRIPT], capture_output=True, text=True
        )
        assert result.stderr == ""

    def test_exact_output_no_extra_lines(self):
        result = subprocess.run(
            [SCRIPT], capture_output=True, text=True
        )
        lines = result.stdout.splitlines()
        assert len(lines) == 1
        assert lines[0] == "hello world"

    def test_executable_without_explicit_bash(self):
        result = subprocess.run(
            [SCRIPT], capture_output=True, text=True
        )
        assert result.returncode == 0

import pathlib
import subprocess

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"


class TestHelloWorldScript:
    def test_prints_hello_world(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.stdout == "hello world\n"

    def test_exit_code_zero(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0

    def test_no_stderr(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.stderr == ""

    def test_exact_output_no_extra_whitespace(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.stdout.strip() == "hello world"
        assert result.stdout == "hello world\n"

    def test_executable_without_bash_prefix(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0

    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

import pathlib
import subprocess

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"


class TestHelloScript:
    def test_prints_hello_world(self):
        result = subprocess.run([str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_executable_permission(self):
        import os
        assert os.access(SCRIPT, os.X_OK)

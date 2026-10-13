import pathlib
import subprocess

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "hello.sh"


class TestHelloSh:
    def test_script_exists(self):
        assert SCRIPT.is_file()

    def test_script_is_executable(self):
        assert SCRIPT.stat().st_mode & 0o111

    def test_prints_hello_world(self):
        result = subprocess.run(
            ["bash", str(SCRIPT)], capture_output=True, text=True, timeout=5
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "Hello, world!"
        assert result.stderr == ""

import os
import stat
import subprocess

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "hello-world", "hello.sh"
)


class TestHelloWorldScript:
    def test_script_exists(self):
        assert os.path.isfile(SCRIPT)

    def test_shebang_line(self):
        with open(SCRIPT) as f:
            first_line = f.readline()
        assert first_line.strip() == "#!/bin/bash"

    def test_executable_permission(self):
        mode = os.stat(SCRIPT).st_mode
        assert mode & stat.S_IXUSR

    def test_output_is_exact(self):
        result = subprocess.run(
            [SCRIPT], capture_output=True, text=True
        )
        assert result.stdout == "hello world\n"

    def test_exit_code_zero(self):
        result = subprocess.run(
            [SCRIPT], capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_no_stderr(self):
        result = subprocess.run(
            [SCRIPT], capture_output=True, text=True
        )
        assert result.stderr == ""

    def test_folder_contains_only_hello_sh(self):
        folder = os.path.dirname(SCRIPT)
        contents = os.listdir(folder)
        assert contents == ["hello.sh"]

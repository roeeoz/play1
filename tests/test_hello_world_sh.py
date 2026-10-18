import os
import pathlib
import stat
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "hello-world" / "hello.sh"


class TestScriptExecution:
    def test_prints_hello_world_and_exits_zero(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True, timeout=5
        )
        assert result.stdout == "hello world\n"
        assert result.returncode == 0


class TestFolderIsolation:
    def test_only_hello_sh_in_directory(self):
        contents = list((REPO_ROOT / "hello-world").iterdir())
        names = [p.name for p in contents]
        assert names == ["hello.sh"]


class TestShebangAndPermissions:
    def test_shebang_line(self):
        first_line = SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/bin/bash"

    def test_executable_permission(self):
        mode = SCRIPT.stat().st_mode
        assert mode & stat.S_IXUSR


class TestOutputExactness:
    def test_no_extra_whitespace_or_lines(self):
        result = subprocess.run(
            [str(SCRIPT)], capture_output=True, timeout=5
        )
        assert result.stdout == b"hello world\n"
        assert result.stderr == b""

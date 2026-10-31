import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = REPO_ROOT / "hello-world"
SCRIPT = SCRIPT_DIR / "hello.sh"


def run_script(cwd=REPO_ROOT, path="./hello-world/hello.sh"):
    return subprocess.run([path], cwd=cwd, capture_output=True, text=True)


class TestLayout:
    def test_folder_exists_at_repo_root(self):
        assert SCRIPT_DIR.is_dir()

    def test_folder_contains_only_hello_sh(self):
        assert sorted(os.listdir(SCRIPT_DIR)) == ["hello.sh"]

    def test_first_line_is_bash_shebang(self):
        assert SCRIPT.read_text().splitlines()[0] == "#!/bin/bash"

    def test_is_executable(self):
        assert os.access(SCRIPT, os.X_OK)

    def test_tracked_by_git_as_executable(self):
        result = subprocess.run(
            ["git", "ls-files", "--stage", "--", "hello-world"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not result.stdout:
            return  # not a git checkout, or not yet staged
        assert [line.split()[0] for line in result.stdout.splitlines()] == ["100755"]
        assert result.stdout.split("\t")[1].strip() == "hello-world/hello.sh"


class TestExecution:
    def test_prints_hello_world_and_exits_zero(self):
        result = run_script()
        assert result.returncode == 0
        assert result.stdout == "hello world\n"
        assert result.stderr == ""

    def test_output_is_a_single_exact_line(self):
        lines = run_script().stdout.splitlines()
        assert lines == ["hello world"]
        assert lines[0] == lines[0].strip()

    def test_runs_from_inside_the_folder(self):
        result = run_script(cwd=SCRIPT_DIR, path="./hello.sh")
        assert result.returncode == 0
        assert result.stdout == "hello world\n"

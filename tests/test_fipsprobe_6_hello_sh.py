"""FIPSPROBE-6: Hello-world bash script in a dedicated folder (verification).

Story-linked proof that ``hello-world/hello.sh`` meets the FIPSPROBE-6
acceptance criteria:

- AC1 (script execution): run directly, it prints "hello world" and exits 0
  -> TestHelloShExecution.test_exits_zero_and_prints_hello_world
- AC2 (direct execution): it starts with ``#!/bin/bash`` and git records it as
  executable (mode 100755), read from the git index rather than the checkout
  (RK1) -> TestHelloShRepositoryShape
- AC3 (output exactness): exactly one line, "hello world", no surrounding
  whitespace, nothing on stderr -> TestHelloShExecution.test_output_is_exactly_one_line
"""

import pathlib
import shutil
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RELPATH = "hello-world/hello.sh"
SCRIPT = REPO_ROOT / "hello-world" / "hello.sh"


def run_script():
    # Executed directly, with no `bash` prefix, so the shebang and mode matter.
    result = subprocess.run(
        [str(SCRIPT)], capture_output=True, text=True, timeout=10, cwd=REPO_ROOT
    )
    return result.returncode, result.stdout, result.stderr


class TestHelloShExecution:
    def test_exits_zero_and_prints_hello_world(self):
        exit_code, stdout, _ = run_script()
        assert exit_code == 0
        assert stdout == "hello world\n"

    def test_output_is_exactly_one_line(self):
        _, stdout, stderr = run_script()
        lines = stdout.splitlines()
        assert lines == ["hello world"]
        assert lines[0] == lines[0].strip()
        assert stderr == ""


class TestHelloShRepositoryShape:
    def test_shebang_is_bin_bash(self):
        first_line = SCRIPT.read_bytes().split(b"\n", 1)[0]
        assert first_line == b"#!/bin/bash"

    def test_git_index_records_executable_mode(self):
        # The checkout's st_mode is unreliable (core.fileMode=false), so read
        # the mode git actually stores. Never skip: a skip would hide RK1.
        if shutil.which("git") is None:
            pytest.fail("git is not on PATH; cannot verify the mode git records for " + RELPATH)
        if not (REPO_ROOT / ".git").exists():
            pytest.fail(f"no .git in {REPO_ROOT}; cannot verify the mode git records for {RELPATH}")
        result = subprocess.run(
            ["git", "ls-files", "-s", "--", RELPATH],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            pytest.fail(f"`git ls-files -s` failed ({result.returncode}): {result.stderr.strip()}")
        entries = result.stdout.splitlines()
        if not entries:
            pytest.fail(f"{RELPATH} is not tracked in the git index")
        assert len(entries) == 1, entries
        meta, path = entries[0].split("\t", 1)
        mode = meta.split()[0]
        assert path == RELPATH
        assert mode == "100755", f"git records {RELPATH} as {mode}, expected 100755"

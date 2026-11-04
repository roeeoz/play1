import pathlib
import subprocess

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "qa" / "s3-hello.sh"


def run_script(args):
    result = subprocess.run(
        [str(SCRIPT)] + args, capture_output=True, text=True, timeout=10
    )
    return result.returncode, result.stdout, result.stderr


class TestNoArguments:
    def test_prints_hello(self):
        exit_code, stdout, stderr = run_script([])
        assert exit_code == 0
        assert stdout == "hello\n"
        assert stderr == ""


class TestScriptShape:
    def test_shebang_then_comment(self):
        content = SCRIPT.read_bytes()
        assert content.startswith(b"#!/bin/sh\n")
        assert content.split(b"\n")[1].startswith(b"#")

    def test_lf_line_endings(self):
        assert b"\r" not in SCRIPT.read_bytes()

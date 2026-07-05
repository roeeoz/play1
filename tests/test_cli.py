import subprocess
import sys


def run_cli(stdin_text: str, args: list = None, env: dict = None):
    import os

    cmd = [sys.executable, "-m", "summarize.cli"] + (args or [])
    base_env = os.environ.copy()
    base_env.pop("OPENAI_API_KEY", None)
    # Ensure the workspace root is on PYTHONPATH so subprocesses find summarize
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    existing = base_env.get("PYTHONPATH", "")
    base_env["PYTHONPATH"] = f"{workspace}:{existing}" if existing else workspace
    if env:
        base_env.update(env)
    result = subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        env=base_env,
    )
    return result


def test_mock_mode_single_line():
    result = run_cli("Hello world")
    assert result.returncode == 0
    assert result.stdout.strip() == "mock summary: Hello world"
    assert result.stderr == ""


def test_mock_mode_first_line_only():
    result = run_cli("Hello world\nLine 2")
    assert result.returncode == 0
    assert result.stdout.strip() == "mock summary: Hello world"


def test_mock_mode_prefix():
    result = run_cli("Some text")
    assert result.returncode == 0
    assert result.stdout.startswith("mock summary:")


def test_empty_stdin_exits_nonzero():
    result = run_cli("")
    assert result.returncode != 0
    assert "No input provided" in result.stderr


def test_whitespace_only_stdin_exits_nonzero():
    result = run_cli("   \n\t\n  ")
    assert result.returncode != 0
    assert "No input provided" in result.stderr


def test_lang_flag_accepted_in_mock_mode():
    result = run_cli("Hello world", args=["--lang", "french"])
    assert result.returncode == 0
    assert result.stdout.startswith("mock summary:")


def test_stderr_empty_on_mock_success():
    result = run_cli("Hello world")
    assert result.returncode == 0
    assert result.stderr == ""


def test_stdout_pipeable():
    """stdout output should end with newline (pipeable to other commands)."""
    result = run_cli("Hello world")
    assert result.returncode == 0
    assert result.stdout.endswith("\n")

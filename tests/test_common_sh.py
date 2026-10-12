import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMON_SH = REPO_ROOT / "scripts" / "lib" / "common.sh"


def _pyproject_version():
    text = (REPO_ROOT / "pyproject.toml").read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert match, "could not parse version from pyproject.toml"
    return match.group(1)


def test_project_version_matches_pyproject():
    result = subprocess.run(
        ["bash", "-c", ". scripts/lib/common.sh; project_version"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"bash failed: {result.stderr}"
    assert result.stdout.strip() == _pyproject_version()


def test_common_sh_has_no_shebang():
    first_line = COMMON_SH.read_text().split("\n", 1)[0]
    assert not first_line.startswith("#!"), "sourced library must not have a shebang"


def test_common_sh_is_not_executable():
    mode = os.stat(COMMON_SH).st_mode
    assert not (mode & 0o111), "sourced library must not be executable"

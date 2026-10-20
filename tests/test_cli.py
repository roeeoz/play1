import subprocess
import sys

import pytest

from testbed_utils import __version__
from testbed_utils.__main__ import main


class TestVersionFlag:
    def test_version_exits_zero(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    def test_version_prints_version_string(self, capsys):
        with pytest.raises(SystemExit):
            main(["--version"])
        out = capsys.readouterr().out
        assert out == __version__ + "\n"

    def test_version_no_stderr(self, capsys):
        with pytest.raises(SystemExit):
            main(["--version"])
        assert capsys.readouterr().err == ""

    def test_version_with_extra_arg_exits_zero(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version", "some-other-arg"])
        assert exc_info.value.code == 0

    def test_version_with_extra_arg_prints_version(self, capsys):
        with pytest.raises(SystemExit):
            main(["--version", "some-other-arg"])
        out = capsys.readouterr().out
        assert out == __version__ + "\n"

    def test_no_version_flag_does_not_exit(self):
        result = main([])
        assert result is None

    def test_subprocess_version(self):
        result = subprocess.run(
            [sys.executable, "-m", "testbed_utils", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == __version__
        assert result.stderr == ""

    def test_subprocess_version_with_extra_arg(self):
        result = subprocess.run(
            [sys.executable, "-m", "testbed_utils", "--version", "extra"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == __version__

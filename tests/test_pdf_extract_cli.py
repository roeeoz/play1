import io
import json
import pathlib
import sys
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from testbed_utils.pdfutils import main

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def run_main(args):
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    exit_code = 0
    with patch("sys.argv", ["pdf-extract"] + args):
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                main()
            except SystemExit as exc:
                exit_code = exc.code if exc.code is not None else 0
    return exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()


class TestPdfExtractCliSuccess:
    def test_exit_code_zero(self):
        exit_code, _, _ = run_main([str(FIXTURES / "sample_form.pdf")])
        assert exit_code == 0

    def test_stdout_is_valid_json(self):
        _, stdout, _ = run_main([str(FIXTURES / "sample_form.pdf")])
        data = json.loads(stdout)
        assert isinstance(data, dict)

    def test_stdout_contains_expected_fields(self):
        _, stdout, _ = run_main([str(FIXTURES / "sample_form.pdf")])
        data = json.loads(stdout)
        assert data["first_name"] == "Alice"
        assert data["last_name"] == "Smith"

    def test_stderr_is_empty(self):
        _, _, stderr = run_main([str(FIXTURES / "sample_form.pdf")])
        assert stderr == ""

    def test_json_is_pretty_printed(self):
        _, stdout, _ = run_main([str(FIXTURES / "sample_form.pdf")])
        assert json.dumps(json.loads(stdout), indent=2) + "\n" == stdout

    def test_no_fields_pdf_outputs_empty_object(self):
        exit_code, stdout, stderr = run_main([str(FIXTURES / "no_fields.pdf")])
        assert exit_code == 0
        assert json.loads(stdout) == {}
        assert stderr == ""


class TestPdfExtractCliError:
    def test_nonexistent_file_exit_code_one(self):
        exit_code, _, _ = run_main(["/nonexistent/path.pdf"])
        assert exit_code == 1

    def test_nonexistent_file_stderr_has_error_prefix(self):
        _, _, stderr = run_main(["/nonexistent/path.pdf"])
        assert "Error:" in stderr

    def test_nonexistent_file_stdout_is_empty(self):
        _, stdout, _ = run_main(["/nonexistent/path.pdf"])
        assert stdout == ""

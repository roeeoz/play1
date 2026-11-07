import json
import pathlib
import subprocess
import sys

import pytest

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "ledger"
SAMPLE = str(FIXTURES / "sample.csv")

MARCH_TEXT = (
    "month: 2026-03\n"
    "base: ILS\n"
    "transactions: 7\n"
    "income: 12925.00\n"
    "expense: -3025.50\n"
    "net: 9899.50\n"
    "categories:\n"
    "  salary: 12000.00 (1)\n"
    "  rent: -1500.00 (1)\n"
    "  freelance: 925.00 (1)\n"
    "  groceries: -760.50 (2)\n"
    "  software: -444.00 (1)\n"
    "  travel: -321.00 (1)\n"
)


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "ledger", *args], capture_output=True, text=True
    )


def test_text_report():
    result = run("report", SAMPLE, "--month", "2026-03")

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == MARCH_TEXT
    assert len(result.stdout.splitlines()) == 13


def test_json_report_with_base_and_top():
    result = run("report", SAMPLE, "--month", "2026-03", "--base", "USD", "--top", "1", "--json")

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "month": "2026-03",
        "base": "USD",
        "count": 7,
        "income": "3493.24",
        "expense": "-817.70",
        "net": "2675.54",
        "categories": [{"name": "salary", "total": "3243.24", "count": 1}],
    }


def test_empty_month():
    result = run("report", SAMPLE, "--month", "2026-05")

    assert result.returncode == 0
    assert result.stdout.endswith(
        "income: 0.00\nexpense: 0.00\nnet: 0.00\ncategories: none\n"
    )


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["report", SAMPLE],
        ["report", SAMPLE, "--month", "2026-13"],
        ["report", SAMPLE, "--month", "2026-03", "--top", "0"],
        ["report", SAMPLE, "--month", "2026-03", "--base", "GBP"],
        ["report", str(FIXTURES / "no_such_file.csv"), "--month", "2026-03"],
    ],
    ids=["no-subcommand", "no-month", "bad-month", "top-zero", "bad-base", "missing-file"],
)
def test_usage_errors_exit_2(args):
    result = run(*args)

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_unreadable_file_message():
    path = str(FIXTURES / "no_such_file.csv")
    result = run("report", path, "--month", "2026-03")

    assert result.stderr.startswith(f"error: cannot read {path}: ")


def test_data_error_exit_3():
    path = str(FIXTURES / "bad_amount.csv")
    result = run("report", path, "--month", "2026-03")

    assert result.returncode == 3
    assert result.stdout == ""
    assert result.stderr == (
        f"error: {path}:3: amount '-2.505' has more than 2 decimal places\n"
    )


def test_help_documents_month():
    result = run("report", "--help")

    assert result.returncode == 0
    assert "--month" in result.stdout


def test_non_utf8_file_is_a_clean_data_error(tmp_path):
    path = tmp_path / "latin1.csv"
    path.write_bytes(
        b"id,date,amount,currency,category,memo\nt1,2026-03-01,5.00,ILS,food,caf\xe9\n"
    )
    result = run("report", str(path), "--month", "2026-03")

    assert result.returncode == 3
    assert result.stdout == ""
    assert result.stderr == f"error: {path}: not valid UTF-8 text\n"


def test_malformed_csv_is_a_clean_data_error(tmp_path):
    path = tmp_path / "huge.csv"
    path.write_text(
        "id,date,amount,currency,category,memo\n"
        "t1,2026-03-01,5.00,ILS,food," + "x" * 200_000 + "\n",
        encoding="utf-8",
    )
    result = run("report", str(path), "--month", "2026-03")

    assert result.returncode == 3
    assert result.stdout == ""
    assert result.stderr.startswith(f"error: {path}: malformed CSV: ")
    assert result.stderr.count("\n") == 1 and "Traceback" not in result.stderr

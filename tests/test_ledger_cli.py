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


def test_json_with_base_and_top():
    result = run("report", SAMPLE, "--month", "2026-03", "--base", "USD", "--top", "1", "--json")
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.endswith("\n")
    assert json.loads(result.stdout) == {
        "month": "2026-03", "base": "USD", "count": 7, "income": "3493.24",
        "expense": "-817.70", "net": "2675.54",
        "categories": [{"name": "salary", "total": "3243.24", "count": 1}],
    }


def test_empty_month():
    result = run("report", SAMPLE, "--month", "2026-05")
    assert result.returncode == 0
    assert result.stdout.splitlines()[-4:] == [
        "income: 0.00", "expense: 0.00", "net: 0.00", "categories: none",
    ]
    assert "transactions: 0\n" in result.stdout


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["report", SAMPLE],
        ["report", SAMPLE, "--month", "2026-13"],
        ["report", SAMPLE, "--month", "2026-03", "--top", "0"],
        ["report", SAMPLE, "--month", "2026-03", "--base", "GBP"],
        ["report", str(FIXTURES / "does_not_exist.csv"), "--month", "2026-03"],
    ],
    ids=["no-subcommand", "no-month", "bad-month", "top-zero", "bad-base", "unreadable-file"],
)
def test_usage_errors(args):
    result = run(*args)
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_unreadable_file_message():
    path = str(FIXTURES / "does_not_exist.csv")
    result = run("report", path, "--month", "2026-03")
    assert result.stderr == f"error: cannot read {path}: No such file or directory\n"


def test_non_utf8_file(tmp_path):
    path = tmp_path / "latin1.csv"
    path.write_bytes(
        b"id,date,amount,currency,category,memo\n"
        b"x1,2026-03-01,10.00,ILS,food,caf\xe9 \xff\n"
    )
    result = run("report", str(path), "--month", "2026-03")
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == f"error: cannot read {path}: not valid UTF-8 text\n"


def test_data_error():
    path = "tests/fixtures/ledger/bad_amount.csv"
    result = subprocess.run(
        [sys.executable, "-m", "ledger", "report", path, "--month", "2026-03"],
        capture_output=True, text=True, cwd=pathlib.Path(__file__).parent.parent,
    )
    assert result.returncode == 3
    assert result.stdout == ""
    assert result.stderr == f"error: {path}:3: amount '-2.505' has more than 2 decimal places\n"


def test_help():
    result = run("report", "--help")
    assert result.returncode == 0
    assert "--month" in result.stdout

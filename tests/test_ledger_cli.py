import json
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "ledger"
SAMPLE = str(FIXTURES / "sample.csv")
BAD_AMOUNT = str(FIXTURES / "bad_amount.csv")


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "ledger", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_text_report():
    result = run("report", SAMPLE, "--month", "2026-03")
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == (
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


def test_json_with_base_and_top():
    result = run("report", SAMPLE, "--month", "2026-03", "--base", "USD", "--top", "1", "--json")
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "month": "2026-03",
        "base": "USD",
        "count": 7,
        "income": "3493.24",
        "expense": "-817.70",
        "net": "2675.54",
        "categories": [{"name": "salary", "total": "3243.24", "count": 1}],
    }
    assert result.stdout.endswith("}\n")


def test_empty_month_tail():
    result = run("report", SAMPLE, "--month", "2026-05")
    assert result.returncode == 0
    assert result.stdout.splitlines()[-4:] == [
        "income: 0.00",
        "expense: 0.00",
        "net: 0.00",
        "categories: none",
    ]


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["report", SAMPLE],
        ["report", SAMPLE, "--month", "2026-13"],
        ["report", SAMPLE, "--month", "2026-03", "--top", "0"],
        ["report", SAMPLE, "--month", "2026-03", "--base", "GBP"],
        ["report", str(FIXTURES / "does-not-exist.csv"), "--month", "2026-03"],
    ],
    ids=["no-subcommand", "no-month", "bad-month", "top-zero", "bad-base", "unreadable-file"],
)
def test_usage_errors(args):
    result = run(*args)
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_unreadable_file_message():
    missing = str(FIXTURES / "does-not-exist.csv")
    result = run("report", missing, "--month", "2026-03")
    assert result.stderr.startswith(f"error: cannot read {missing}: ")


def test_data_error():
    result = run("report", BAD_AMOUNT, "--month", "2026-03")
    assert result.returncode == 3
    assert result.stdout == ""
    assert result.stderr == f"error: {BAD_AMOUNT}:3: amount '-2.505' has more than 2 decimal places\n"


def test_help():
    result = run("report", "--help")
    assert result.returncode == 0
    assert "--month" in result.stdout

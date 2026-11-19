"""End-to-end tests for ``python -m ledger report`` (SCRUM-34 t3).

Every case runs the installed package through a subprocess.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE = "tests/fixtures/ledger/sample.csv"
BAD = "tests/fixtures/ledger/bad_amount.csv"


def run(*args):
    result = subprocess.run(
        [sys.executable, "-m", "ledger", *args],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO_ROOT,
    )
    return result.returncode, result.stdout, result.stderr


def test_text_report():
    code, out, err = run("report", SAMPLE, "--month", "2026-03")
    assert (code, err) == (0, "")
    assert out == (
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
    code, out, err = run("report", SAMPLE, "--month", "2026-03", "--base", "USD", "--top", "1", "--json")
    assert (code, err) == (0, "")
    assert out.endswith("\n") and out.count("\n") == 1
    assert json.loads(out) == {
        "month": "2026-03",
        "base": "USD",
        "count": 7,
        "income": "3493.24",
        "expense": "-817.70",
        "net": "2675.54",
        "categories": [{"name": "salary", "total": "3243.24", "count": 1}],
    }


def test_empty_month():
    code, out, err = run("report", SAMPLE, "--month", "2026-05")
    assert (code, err) == (0, "")
    assert out.endswith("income: 0.00\nexpense: 0.00\nnet: 0.00\ncategories: none\n")


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["report", SAMPLE],
        ["report", SAMPLE, "--month", "2026-13"],
        ["report", SAMPLE, "--month", "2026-03", "--top", "0"],
        ["report", SAMPLE, "--month", "2026-03", "--top", "x"],
        ["report", SAMPLE, "--month", "2026-03", "--base", "GBP"],
        ["report", "tests/fixtures/ledger/does-not-exist.csv", "--month", "2026-03"],
    ],
    ids=["no-subcommand", "no-month", "bad-month", "top-0", "top-not-int", "bad-base", "missing-file"],
)
def test_usage_errors_exit_2(args):
    code, out, err = run(*args)
    assert code == 2
    assert out == ""
    assert err.strip()


def test_directory_file_exits_2(tmp_path):
    code, out, err = run("report", str(tmp_path), "--month", "2026-03")
    assert (code, out) == (2, "")
    assert err.strip()


def test_non_utf8_file_exits_2(tmp_path):
    path = tmp_path / "latin1.csv"
    path.write_bytes(b"id,date,amount,currency,category,memo\nt1,2026-03-01,5,ILS,caf\xe9,m\n")
    code, out, err = run("report", str(path), "--month", "2026-03")
    assert (code, out) == (2, "")
    assert err.strip()


def test_base_defaults_to_ils_and_accepts_each_currency():
    for base in ("ILS", "USD", "EUR"):
        code, out, _ = run("report", SAMPLE, "--month", "2026-03", "--base", base)
        assert code == 0 and f"base: {base}\n" in out
    assert "base: ILS\n" in run("report", SAMPLE, "--month", "2026-03")[1]


def test_data_error_exits_3_with_path_as_given():
    code, out, err = run("report", BAD, "--month", "2026-03")
    assert (code, out) == (3, "")
    assert err == f"error: {BAD}:3: amount '-2.505' has more than 2 decimal places\n"

    absolute = str(REPO_ROOT / BAD)
    code, out, err = run("report", absolute, "--month", "2026-03")
    assert (code, out) == (3, "")
    assert err == f"error: {absolute}:3: amount '-2.505' has more than 2 decimal places\n"


def test_report_help():
    code, out, _ = run("report", "--help")
    assert code == 0
    assert "--month" in out


def test_output_is_deterministic():
    for args in (["--month", "2026-03"], ["--month", "2026-03", "--base", "EUR", "--json"]):
        first = subprocess.run(
            [sys.executable, "-m", "ledger", "report", SAMPLE, *args], capture_output=True, cwd=REPO_ROOT
        )
        second = subprocess.run(
            [sys.executable, "-m", "ledger", "report", SAMPLE, *args], capture_output=True, cwd=REPO_ROOT
        )
        assert first.returncode == 0
        assert first.stdout == second.stdout

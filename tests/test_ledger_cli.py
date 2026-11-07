import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "ledger"
SAMPLE = str(FIXTURES / "sample.csv")


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "ledger", *args],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )


def test_text_report():
    result = run("report", "tests/fixtures/ledger/sample.csv", "--month", "2026-03")
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
    result = run("report", SAMPLE, "--month", "2026-03",
                 "--base", "USD", "--top", "1", "--json")
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "month": "2026-03", "base": "USD", "count": 7, "income": "3493.24",
        "expense": "-817.70", "net": "2675.54",
        "categories": [{"name": "salary", "total": "3243.24", "count": 1}],
    }


def test_empty_month():
    result = run("report", SAMPLE, "--month", "2026-05")
    assert result.returncode == 0
    assert result.stdout.endswith(
        "income: 0.00\nexpense: 0.00\nnet: 0.00\ncategories: none\n")


def test_explicit_base_ils_matches_default():
    default = run("report", SAMPLE, "--month", "2026-03")
    explicit = run("report", SAMPLE, "--month", "2026-03", "--base", "ILS")
    assert explicit.returncode == 0
    assert explicit.stdout == default.stdout


def test_eur_base_accepted():
    result = run("report", SAMPLE, "--month", "2026-03", "--base", "EUR")
    assert result.returncode == 0
    assert "base: EUR\n" in result.stdout


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["report", SAMPLE],
        ["report", SAMPLE, "--month", "2026-13"],
        ["report", SAMPLE, "--month", "2026-03", "--top", "0"],
        ["report", SAMPLE, "--month", "2026-03", "--top", "x"],
        ["report", SAMPLE, "--month", "2026-03", "--base", "GBP"],
        ["report", "no/such/ledger.csv", "--month", "2026-03"],
        ["report", str(FIXTURES), "--month", "2026-03"],
    ],
    ids=["no-subcommand", "no-month", "bad-month", "top-0", "top-text",
         "bad-base", "missing-file", "directory"],
)
def test_usage_errors(args):
    result = run(*args)
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip()
    assert "Traceback" not in result.stderr


def test_undecodable_file_is_usage_error(tmp_path):
    bad = tmp_path / "latin1.csv"
    bad.write_bytes(b"id,date,amount,currency,category,memo\n"
                    b"t1,2026-03-01,1.00,ILS,caf\xe9,m\n")
    result = run("report", str(bad), "--month", "2026-03")
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip()
    assert "Traceback" not in result.stderr


def test_data_error():
    path = "tests/fixtures/ledger/bad_amount.csv"
    result = run("report", path, "--month", "2026-03")
    assert result.returncode == 3
    assert result.stdout == ""
    assert result.stderr == (
        f"error: {path}:3: amount '-2.505' has more than 2 decimal places\n")


def test_data_error_echoes_path_as_typed():
    path = "./tests/fixtures/ledger/../ledger/bad_amount.csv"
    result = run("report", path, "--month", "2026-03")
    assert result.returncode == 3
    assert result.stderr.startswith(f"error: {path}:3: ")


def test_help_documents_month():
    result = run("report", "--help")
    assert result.returncode == 0
    assert "--month" in result.stdout


def test_deterministic_output():
    args = ("report", SAMPLE, "--month", "2026-03", "--base", "USD", "--json")
    assert run(*args).stdout == run(*args).stdout

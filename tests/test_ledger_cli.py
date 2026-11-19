import json
import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SAMPLE = "tests/fixtures/ledger/sample.csv"
BAD_AMOUNT = "tests/fixtures/ledger/bad_amount.csv"

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
        [sys.executable, "-m", "ledger", *args],
        capture_output=True,
        timeout=30,
        cwd=REPO_ROOT,
    )


class TestSuccess:
    def test_text_report(self):
        first = run("report", SAMPLE, "--month", "2026-03")
        assert first.returncode == 0
        assert first.stderr == b""
        assert first.stdout.decode() == MARCH_TEXT
        assert len(first.stdout.decode().splitlines()) == 13
        second = run("report", SAMPLE, "--month", "2026-03")
        assert second.stdout == first.stdout

    def test_json_with_base_and_top(self):
        result = run("report", SAMPLE, "--month", "2026-03", "--base", "USD", "--top", "1", "--json")
        assert result.returncode == 0
        assert result.stderr == b""
        assert json.loads(result.stdout) == {
            "month": "2026-03", "base": "USD", "count": 7, "income": "3493.24",
            "expense": "-817.70", "net": "2675.54",
            "categories": [{"name": "salary", "total": "3243.24", "count": 1}],
        }

    def test_base_defaults_to_ils_and_accepts_eur(self):
        assert b"base: ILS\n" in run("report", SAMPLE, "--month", "2026-03").stdout
        result = run("report", SAMPLE, "--month", "2026-03", "--base", "EUR")
        assert result.returncode == 0 and b"base: EUR\n" in result.stdout

    def test_empty_month(self):
        result = run("report", SAMPLE, "--month", "2026-05")
        assert result.returncode == 0
        assert result.stderr == b""
        assert result.stdout.decode().endswith(
            "income: 0.00\nexpense: 0.00\nnet: 0.00\ncategories: none\n")

    def test_help(self):
        result = run("report", "--help")
        assert result.returncode == 0
        out = result.stdout.decode()
        for option in ("--month", "--base", "--top", "--json"):
            assert option in out


class TestUsageErrors:
    @pytest.mark.parametrize(
        "args",
        [
            [],
            ["report", SAMPLE],
            ["report", SAMPLE, "--month", "2026-13"],
            ["report", SAMPLE, "--month", "2026-03", "--top", "0"],
            ["report", SAMPLE, "--month", "2026-03", "--top", "x"],
            ["report", SAMPLE, "--month", "2026-03", "--base", "GBP"],
            ["report", "tests/fixtures/ledger/missing.csv", "--month", "2026-03"],
            ["report", "tests/fixtures/ledger", "--month", "2026-03"],
        ],
        ids=["no-subcommand", "no-month", "bad-month", "top-0", "top-text", "bad-base",
             "missing-file", "directory"],
    )
    def test_exit_2(self, args):
        result = run(*args)
        assert result.returncode == 2
        assert result.stdout == b""
        assert result.stderr.strip() != b""

    def test_invalid_utf8_file(self, tmp_path):
        path = tmp_path / "bad.csv"
        path.write_bytes(b"id,date,amount,currency,category,memo\n"
                         b"t1,2026-03-01,1,ILS,\xff\xfe,m\n")
        result = run("report", str(path), "--month", "2026-03")
        assert result.returncode == 2
        assert result.stdout == b""
        assert result.stderr.strip() != b""


class TestDataError:
    def test_bad_amount(self):
        result = run("report", BAD_AMOUNT, "--month", "2026-03")
        assert result.returncode == 3
        assert result.stdout == b""
        assert result.stderr.decode() == (
            "error: tests/fixtures/ledger/bad_amount.csv:3: "
            "amount '-2.505' has more than 2 decimal places\n")

    def test_file_echoed_as_given(self):
        result = run("report", "./" + BAD_AMOUNT, "--month", "2026-03", "--json")
        assert result.returncode == 3
        assert result.stdout == b""
        assert result.stderr.decode().startswith("error: ./tests/fixtures/ledger/bad_amount.csv:3: ")

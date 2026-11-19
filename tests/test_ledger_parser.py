"""Tests for the ledger CSV parser (SCRUM-34 t1)."""

import dataclasses
import io
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ledger import LedgerError, Transaction, parse_csv, parse_lines

FIXTURES = Path(__file__).parent / "fixtures" / "ledger"
HEADER = "id,date,amount,currency,category,memo\n"
GOOD = "t1,2026-03-01,10.00,ILS,food,lunch\n"


def parse_text(text):
    return parse_lines(io.StringIO(text))


def error_of(text):
    with pytest.raises(LedgerError) as info:
        parse_text(text)
    return info.value


def test_sample_parses_nine_typed_transactions_in_order():
    txs = parse_csv(FIXTURES / "sample.csv")
    assert [t.id for t in txs] == [f"t00{i}" for i in range(1, 10)]
    for t in txs:
        assert isinstance(t, Transaction)
        assert isinstance(t.id, str)
        assert isinstance(t.date, date)
        assert isinstance(t.amount, Decimal)
        assert isinstance(t.currency, str)
        assert isinstance(t.category, str)
        assert isinstance(t.memo, str)
    salary = txs[1]
    assert salary.amount == Decimal("12000.00")
    assert str(salary.amount) == "12000.00"
    assert salary.date == date(2026, 3, 1)
    assert txs[2].memo == ""
    assert sum(1 for t in txs if (t.date.year, t.date.month) == (2026, 3)) == 7
    with pytest.raises(dataclasses.FrozenInstanceError):
        salary.amount = Decimal("1")  # type: ignore[misc]


def test_header_order_is_free_fields_stripped_and_extra_columns_ignored():
    text = (
        " memo , category,currency,amount,date,id,extra\n"
        "  a note , food ,  USD , -3.50 , 2026-03-04 , x1 , ignored\n"
    )
    assert parse_text(text) == [
        Transaction("x1", date(2026, 3, 4), Decimal("-3.50"), "USD", "food", "a note")
    ]


def test_bom_blank_lines_and_quoted_memo():
    txs = parse_csv(FIXTURES / "bom_blank.csv")
    assert [t.id for t in txs] == ["b1", "b2"]
    assert txs[0].memo == ""
    assert txs[1].memo == "lunch, with team"


def test_header_only_gives_empty_list():
    assert parse_text(HEADER) == []


@pytest.mark.parametrize(
    "row, reason",
    [
        ("t1,2026-3-1,1,ILS,c,m", "date '2026-3-1' is not YYYY-MM-DD"),
        ("t1,20260301,1,ILS,c,m", "date '20260301' is not YYYY-MM-DD"),
        ("t1,2026-02-30,1,ILS,c,m", "date '2026-02-30' is not a calendar date"),
        ("t1,2026-03-01,abc,ILS,c,m", "amount 'abc' is not a number"),
        ("t1,2026-03-01,NaN,ILS,c,m", "amount 'NaN' is not a number"),
        ("t1,2026-03-01,Infinity,ILS,c,m", "amount 'Infinity' is not a number"),
        ("t1,2026-03-01,1.505,ILS,c,m", "amount '1.505' has more than 2 decimal places"),
        ("t1,2026-03-01,0,ILS,c,m", "amount must not be zero"),
        ("t1,2026-03-01,1,usd,c,m", "unknown currency 'usd'"),
        ("t1,2026-03-01,1,,c,m", "unknown currency ''"),
        ("t1,2026-03-01,1,ILS,,m", "empty category"),
        (",2026-03-01,1,ILS,c,m", "empty id"),
        ("t1,2026-03-01,1,ILS,c", "expected 6 fields, got 5"),
        (",,,,,", "empty id"),
    ],
)
def test_bad_row_reasons(row, reason):
    err = error_of(HEADER + row + "\n")
    assert (err.line, err.reason) == (2, reason)
    assert str(err) == f"line 2: {reason}"


@pytest.mark.parametrize(
    "amount, reason",
    [
        ("1e2", "amount '1e2' is not a number"),
        ('"1,000"', "amount '1,000' is not a number"),
        ("1_000", "amount '1_000' is not a number"),
        (".5", "amount '.5' is not a number"),
        ("5.", "amount '5.' is not a number"),
        ("١٢", "amount '١٢' is not a number"),
        ("", "amount '' is not a number"),
        ("1.500", "amount '1.500' has more than 2 decimal places"),
        ("0", "amount must not be zero"),
        ("-0", "amount must not be zero"),
        ("0.00", "amount must not be zero"),
    ],
)
def test_amount_spellings_rejected(amount, reason):
    err = error_of(HEADER + f"t1,2026-03-01,{amount},ILS,c,m\n")
    assert (err.line, err.reason) == (2, reason)


def test_signed_amount_accepted():
    (tx,) = parse_text(HEADER + "t1,2026-03-01,+5,ILS,c,m\n")
    assert tx.amount == Decimal("5")


def test_parsing_stops_at_first_bad_row():
    err = error_of(HEADER + GOOD + "t2,bad,abc,xxx,,\n" + "t3,2026-03-01,0,ILS,c,m\n")
    assert (err.line, err.reason) == (3, "date 'bad' is not YYYY-MM-DD")


def test_validation_order_within_row():
    # every field is bad; id checks come first, then date, amount, currency, category
    assert error_of(HEADER + "t1,x,y,z,,m\n").reason == "date 'x' is not YYYY-MM-DD"
    assert error_of(HEADER + "t1,2026-03-01,y,z,,m\n").reason == "amount 'y' is not a number"
    assert error_of(HEADER + "t1,2026-03-01,1,z,,m\n").reason == "unknown currency 'z'"
    assert error_of(HEADER + GOOD + "t1,x,y,z,,m\n").reason.startswith("duplicate id")
    assert error_of(HEADER + ",x,y,z,,m,extra\n").reason == "expected 6 fields, got 7"


def test_field_count_uses_header_field_count():
    err = error_of("id,date,amount,currency,category,memo,note\n" + GOOD)
    assert err.reason == "expected 7 fields, got 6"


def test_duplicate_id_across_blank_line():
    err = error_of(HEADER + GOOD + "\n" + "t1,2026-03-02,5,ILS,c,m\n")
    assert err.line == 4
    assert err.reason == "duplicate id 't1' (first seen on line 2)"


def test_missing_columns_listed_in_canonical_order():
    err = error_of("memo,amount,date,id\n")
    assert (err.line, err.reason) == (1, "missing column(s): currency, category")
    err = error_of("date,id,amount\n")
    assert (err.line, err.reason) == (1, "missing column(s): currency, category, memo")


def test_duplicate_required_column():
    err = error_of("id,date,amount,amount,currency,category,memo\n")
    assert (err.line, err.reason) == (1, "duplicate column 'amount'")


def test_empty_file_is_missing_header():
    with pytest.raises(LedgerError) as info:
        parse_csv(FIXTURES / "empty.csv")
    assert (info.value.line, info.value.reason) == (1, "missing header")
    assert str(info.value) == "line 1: missing header"


def test_blank_only_input_is_missing_header():
    err = error_of("\n   \n\n")
    assert (err.line, err.reason) == (1, "missing header")


def test_leading_blank_lines_before_header_count():
    err = error_of("\n\n" + HEADER + "t1,2026-03-01,0,ILS,c,m\n")
    assert err.line == 4


def test_multiline_quoted_memo_reports_start_line():
    text = HEADER + 't1,2026-03-01,5,ILS,c,"two\nlines"\n' + "t2,2026-03-01,0,ILS,c,m\n"
    err = error_of(text)
    assert err.line == 4
    err = error_of(HEADER + 't1,2026-03-01,0,ILS,c,"two\nlines"\n')
    assert err.line == 2


def test_parse_lines_matches_parse_csv():
    path = FIXTURES / "bom_blank.csv"
    expected = parse_csv(path)
    text = path.read_bytes().decode("utf-8")  # BOM kept as U+FEFF
    assert text.startswith("\ufeff")
    assert parse_lines(io.StringIO(text, newline="")) == expected
    assert parse_lines(text.splitlines(keepends=True)) == expected
    assert parse_lines(list(open(FIXTURES / "sample.csv", encoding="utf-8"))) == parse_csv(
        FIXTURES / "sample.csv"
    )

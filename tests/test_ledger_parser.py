import dataclasses
import datetime
import io
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


class TestSample:
    def test_nine_transactions_in_file_order(self):
        txs = parse_csv(FIXTURES / "sample.csv")
        assert [t.id for t in txs] == [f"t00{i}" for i in range(1, 10)]
        months = [(t.date.year, t.date.month) for t in txs]
        assert months.count((2026, 3)) == 7
        assert txs[0].date == datetime.date(2026, 2, 27)
        assert txs[-1].date == datetime.date(2026, 4, 1)

    def test_typed_fields(self):
        salary = parse_csv(FIXTURES / "sample.csv")[1]
        assert salary == Transaction(
            id="t002",
            date=datetime.date(2026, 3, 1),
            amount=Decimal("12000.00"),
            currency="ILS",
            category="salary",
            memo="March salary",
        )
        assert str(salary.amount) == "12000.00"

    def test_empty_memo_and_frozen(self):
        rent = parse_csv(FIXTURES / "sample.csv")[2]
        assert rent.memo == ""
        with pytest.raises(dataclasses.FrozenInstanceError):
            rent.amount = Decimal("1")


class TestHeader:
    def test_columns_matched_by_name_and_fields_trimmed(self):
        text = (
            " memo , category,currency,amount,date,id ,extra\n"
            "  hello  , food ,  USD , -1.50 , 2026-03-04 ,  x9 , ignored\n"
        )
        assert parse_text(text) == [
            Transaction("x9", datetime.date(2026, 3, 4), Decimal("-1.50"),
                        "USD", "food", "hello")
        ]

    def test_repeated_column_first_wins(self):
        text = "id,date,amount,currency,category,memo,category\n" \
               "t1,2026-03-01,1.00,ILS,first,m,second\n"
        assert parse_text(text)[0].category == "first"

    def test_header_names_case_sensitive(self):
        err = error_of("ID,date,amount,currency,category,memo\n")
        assert (err.line, err.reason) == (1, "missing column(s): id")

    def test_missing_columns_canonical_order(self):
        err = error_of("memo,amount,id,date\n")
        assert (err.line, err.reason) == (1, "missing column(s): currency, category")
        err = error_of("date,id,amount\n")
        assert (err.line, err.reason) == (1, "missing column(s): currency, category, memo")
        assert str(err) == "line 1: missing column(s): currency, category, memo"

    def test_empty_file_missing_header(self):
        assert (FIXTURES / "empty.csv").read_bytes() == b""
        with pytest.raises(LedgerError) as info:
            parse_csv(FIXTURES / "empty.csv")
        assert (info.value.line, info.value.reason) == (1, "missing header")

    def test_only_blank_lines_missing_header(self):
        err = error_of("\n   \n\n")
        assert (err.line, err.reason) == (1, "missing header")

    def test_header_only_is_empty_list(self):
        assert parse_text(HEADER) == []

    def test_blank_lines_before_header(self):
        err = error_of("\n  \n" + HEADER + "\n" + "t1,2026-03-01,bad,ILS,f,m\n")
        assert err.line == 5
        assert len(parse_text("\n  \n" + HEADER + GOOD)) == 1


class TestBomAndBlankLines:
    def test_fixture_bytes_are_intact(self):
        raw = (FIXTURES / "bom_blank.csv").read_bytes()
        assert raw.startswith(b"\xef\xbb\xbf")
        assert b"\r\n\r\n   \r\n" in raw

    def test_bom_blank_parses_two(self):
        txs = parse_csv(FIXTURES / "bom_blank.csv")
        assert [t.id for t in txs] == ["b1", "b2"]
        assert txs[0].memo == ""
        assert txs[1].memo == "Novel, used"

    def test_stream_with_bom_matches_file(self):
        text = (FIXTURES / "bom_blank.csv").read_bytes().decode("utf-8")
        assert text.startswith("﻿")
        stream = io.StringIO(text, newline="")
        assert parse_lines(stream) == parse_csv(FIXTURES / "bom_blank.csv")

    def test_sample_stream_matches_file(self):
        text = (FIXTURES / "sample.csv").read_text(encoding="utf-8")
        assert parse_text(text) == parse_csv(FIXTURES / "sample.csv")


def row(id="t1", date="2026-03-01", amount="10.00", currency="ILS",
        category="food", memo="m"):
    return HEADER + f"{id},{date},{amount},{currency},{category},{memo}\n"


@pytest.mark.parametrize(
    "text, reason",
    [
        (row(date="2026-3-1"), "date '2026-3-1' is not YYYY-MM-DD"),
        (row(date="20260301"), "date '20260301' is not YYYY-MM-DD"),
        (row(date="２０２６-03-01"), "date '２０２６-03-01' is not YYYY-MM-DD"),
        (row(date="2026-02-30"), "date '2026-02-30' is not a calendar date"),
        (row(date="2026-13-01"), "date '2026-13-01' is not a calendar date"),
        (row(amount="abc"), "amount 'abc' is not a number"),
        (row(amount="NaN"), "amount 'NaN' is not a number"),
        (row(amount="Infinity"), "amount 'Infinity' is not a number"),
        (row(amount="1E+3"), "amount '1E+3' is not a number"),
        (row(amount="1_000"), "amount '1_000' is not a number"),
        (row(amount="１０"), "amount '１０' is not a number"),
        (row(amount=""), "amount '' is not a number"),
        (row(amount="1.505"), "amount '1.505' has more than 2 decimal places"),
        (row(amount="0"), "amount must not be zero"),
        (row(amount="-0.00"), "amount must not be zero"),
        (row(currency="usd"), "unknown currency 'usd'"),
        (row(currency="GBP"), "unknown currency 'GBP'"),
        (row(category=" "), "empty category"),
        (row(id=" "), "empty id"),
        (HEADER + "t1,2026-03-01,10.00,ILS,food\n", "expected 6 fields, got 5"),
        ("id,date,amount,currency,category,memo,x\n"
         "t1,2026-03-01,10.00,ILS,food\n", "expected 7 fields, got 5"),
    ],
)
def test_bad_row_reasons(text, reason):
    err = error_of(text)
    assert (err.line, err.reason) == (2, reason)
    assert str(err) == f"line 2: {reason}"


@pytest.mark.parametrize(
    "fields, reason",
    [
        ("t1,2026-03-01,10.00,ILS,food", "expected 6 fields, got 5"),
        (",bad,abc,usd,,m", "empty id"),
        ("t1,bad,abc,usd,,m", "date 'bad' is not YYYY-MM-DD"),
        ("t1,2026-03-01,abc,usd,,m", "amount 'abc' is not a number"),
        ("t1,2026-03-01,1.00,usd,,m", "unknown currency 'usd'"),
        ("t0,2026-03-01,1.00,ILS,,m", "empty category"),
    ],
)
def test_check_order(fields, reason):
    err = error_of(row(id="t0") + fields + "\n")
    assert (err.line, err.reason) == (3, reason)


def test_duplicate_id_after_blank_line():
    err = error_of(HEADER + GOOD + "\n" + "t1,2026-03-02,5.00,ILS,food,again\n")
    assert (err.line, err.reason) == (4, "duplicate id 't1' (first seen on line 2)")


def test_stops_at_first_bad_row():
    err = error_of(HEADER + GOOD + "t2,x,1,ILS,f,m\n" + "t3,2026-03-01,abc,ILS,f,m\n")
    assert err.line == 3


def test_multiline_memo_line_numbers():
    text = (HEADER
            + 't1,2026-03-01,1.00,ILS,f,"line one\nline two"\n'
            + 't2,2026-03-01,1.00,ILS,f,"a\nb\nc"\n'
            + "t3,2026-03-01,abc,ILS,f,m\n")
    err = error_of(text)
    assert err.line == 7
    bad_multiline = HEADER + GOOD + 't2,2026-03-01,1.555,ILS,f,"x\ny"\n'
    assert error_of(bad_multiline).line == 3


def test_bad_amount_fixture():
    with pytest.raises(LedgerError) as info:
        parse_csv(FIXTURES / "bad_amount.csv")
    assert info.value.line == 3
    assert info.value.reason == "amount '-2.505' has more than 2 decimal places"

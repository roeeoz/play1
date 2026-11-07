import datetime
import io
import pathlib
from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from ledger import COLUMNS, CURRENCIES, LedgerError, Transaction, parse_csv, parse_lines

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "ledger"
HEADER = "id,date,amount,currency,category,memo\n"
VALID_ROW = "t1,2026-03-01,10.00,ILS,food,lunch\n"


def parse_text(text):
    return parse_lines(io.StringIO(text))


def test_constants():
    assert CURRENCIES == ("ILS", "USD", "EUR")
    assert COLUMNS == ("id", "date", "amount", "currency", "category", "memo")


def test_sample_file_parses_in_order():
    transactions = parse_csv(FIXTURES / "sample.csv")
    assert [t.id for t in transactions] == [f"t00{i}" for i in range(1, 10)]
    first = transactions[0]
    assert first == Transaction(
        "t001", datetime.date(2026, 3, 1), Decimal("12000.00"), "ILS", "salary", "March salary"
    )
    assert str(first.amount) == "12000.00"
    assert transactions[2].amount == Decimal("-120") and transactions[2].currency == "USD"
    assert transactions[4].memo == ""
    assert transactions[5].memo == "Logo design, invoice 7"
    assert transactions[7].date == datetime.date(2026, 2, 27)
    assert transactions[8].date == datetime.date(2026, 4, 1)
    assert sum(t.date.month == 3 for t in transactions) == 7


def test_transaction_is_frozen():
    transaction = parse_text(HEADER + VALID_ROW)[0]
    with pytest.raises(FrozenInstanceError):
        transaction.amount = Decimal("1")


def test_header_order_is_free_and_fields_are_stripped():
    text = (
        "memo , category,currency,amount,date,id,extra\n"
        "  a note , food ,  USD , -3.5 , 2026-03-07 ,  x1 , ignored\n"
    )
    assert parse_text(text) == [
        Transaction("x1", datetime.date(2026, 3, 7), Decimal("-3.5"), "USD", "food", "a note")
    ]


def test_bom_blank_lines_and_quoted_memo():
    transactions = parse_csv(FIXTURES / "bom_blank.csv")
    assert [t.id for t in transactions] == ["b1", "b2"]
    assert transactions[0].memo == ""
    assert transactions[1].memo == "Flowers, chocolate"
    assert transactions[1].amount == Decimal("20")


def test_header_only_yields_empty_list():
    assert parse_text(HEADER) == []


@pytest.mark.parametrize(
    "row, reason",
    [
        ("t2,2026-3-1,1,ILS,food,", "date '2026-3-1' is not YYYY-MM-DD"),
        ("t2,2026-02-30,1,ILS,food,", "date '2026-02-30' is not a calendar date"),
        ("t2,2026-03-01,abc,ILS,food,", "amount 'abc' is not a number"),
        ("t2,2026-03-01,NaN,ILS,food,", "amount 'NaN' is not a number"),
        ("t2,2026-03-01,Infinity,ILS,food,", "amount 'Infinity' is not a number"),
        ("t2,2026-03-01,1e2,ILS,food,", "amount '1e2' is not a number"),
        ("t2,2026-03-01,1.505,ILS,food,", "amount '1.505' has more than 2 decimal places"),
        ("t2,2026-03-01,0.00,ILS,food,", "amount must not be zero"),
        ("t2,2026-03-01,1,usd,food,", "unknown currency 'usd'"),
        ("t2,2026-03-01,1,GBP,food,", "unknown currency 'GBP'"),
        ("t2,2026-03-01,1,ILS, ,", "empty category"),
        (",2026-03-01,1,ILS,food,", "empty id"),
        ("t2,2026-03-01,1,ILS,food", "expected 6 fields, got 5"),
    ],
)
def test_bad_row_reasons(row, reason):
    text = HEADER + VALID_ROW + row + "\n" + "t3,bad,1,ILS,food,\n"
    with pytest.raises(LedgerError) as caught:
        parse_text(text)
    error = caught.value
    assert (error.line, error.reason) == (3, reason)
    assert str(error) == f"line 3: {reason}"


def test_valid_control_rows_parse():
    assert len(parse_text(HEADER + VALID_ROW + "t2,2026-03-01,-.5,EUR,food,\n")) == 2


def test_duplicate_id_names_both_lines():
    text = HEADER + "t1,2026-03-01,1,ILS,food,\n\nt1,2026-03-02,2,ILS,food,\n"
    with pytest.raises(LedgerError) as caught:
        parse_text(text)
    assert caught.value.line == 4
    assert caught.value.reason == "duplicate id 't1' (first seen on line 2)"


def test_line_numbers_count_blank_and_multiline_records():
    text = HEADER + '\n  \nt1,2026-03-01,1,ILS,food,"two\nlines"\n\nt2,2026-03-01,x,ILS,food,\n'
    with pytest.raises(LedgerError) as caught:
        parse_text(text)
    assert str(caught.value) == "line 7: amount 'x' is not a number"


def test_missing_columns_in_canonical_order():
    with pytest.raises(LedgerError) as caught:
        parse_text("amount,id,date\n")
    assert (caught.value.line, caught.value.reason) == (
        1,
        "missing column(s): currency, category, memo",
    )


def test_empty_file_is_missing_header():
    with pytest.raises(LedgerError) as caught:
        parse_csv(FIXTURES / "empty.csv")
    assert (caught.value.line, caught.value.reason) == (1, "missing header")
    assert str(caught.value) == "line 1: missing header"


def test_bad_amount_fixture_fails_on_line_3():
    with pytest.raises(LedgerError) as caught:
        parse_csv(FIXTURES / "bad_amount.csv")
    assert str(caught.value) == "line 3: amount '-2.505' has more than 2 decimal places"


def test_parse_lines_matches_parse_csv():
    path = FIXTURES / "sample.csv"
    assert parse_lines(io.StringIO(path.read_text(encoding="utf-8"))) == parse_csv(path)

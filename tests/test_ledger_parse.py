import datetime
import io
from dataclasses import FrozenInstanceError
from decimal import Decimal
from pathlib import Path

import pytest

from ledger import COLUMNS, CURRENCIES, LedgerError, Transaction, parse_csv, parse_lines

FIXTURES = Path(__file__).parent / "fixtures" / "ledger"
HEADER = "id,date,amount,currency,category,memo\n"
VALID_ROW = "t1,2026-03-01,10.00,ILS,food,lunch\n"


def parse_text(text):
    return parse_lines(io.StringIO(text))


def error_of(text):
    with pytest.raises(LedgerError) as info:
        parse_text(text)
    return info.value


class TestModel:
    def test_currencies(self):
        assert CURRENCIES == ("ILS", "USD", "EUR")

    def test_columns_canonical_order(self):
        assert COLUMNS == ("id", "date", "amount", "currency", "category", "memo")

    def test_transaction_is_frozen(self):
        tx = parse_text(HEADER + VALID_ROW)[0]
        with pytest.raises(FrozenInstanceError):
            tx.amount = Decimal("1")

    def test_ledger_error_fields_and_str(self):
        err = LedgerError(4, "empty id")
        assert isinstance(err, Exception)
        assert err.line == 4
        assert err.reason == "empty id"
        assert str(err) == "line 4: empty id"


class TestSampleFile:
    def test_parses_nine_rows_in_order(self):
        txs = parse_csv(FIXTURES / "sample.csv")
        assert [tx.id for tx in txs] == [f"t00{i}" for i in range(1, 10)]
        assert all(isinstance(tx, Transaction) for tx in txs)

    def test_first_row_exact_values(self):
        tx = parse_csv(FIXTURES / "sample.csv")[0]
        assert tx == Transaction(
            id="t001",
            date=datetime.date(2026, 3, 1),
            amount=Decimal("12000.00"),
            currency="ILS",
            category="salary",
            memo="March salary",
        )
        assert str(tx.amount) == "12000.00"

    def test_types_and_months(self):
        txs = parse_csv(FIXTURES / "sample.csv")
        for tx in txs:
            assert isinstance(tx.date, datetime.date)
            assert isinstance(tx.amount, Decimal)
        months = [tx.date.strftime("%Y-%m") for tx in txs]
        assert months.count("2026-03") == 7
        assert months.count("2026-02") == 1
        assert months.count("2026-04") == 1

    def test_empty_memo(self):
        txs = parse_csv(FIXTURES / "sample.csv")
        assert txs[6].memo == ""

    def test_accepts_str_path(self):
        assert len(parse_csv(str(FIXTURES / "sample.csv"))) == 9


class TestHeaderAndFields:
    def test_header_order_free_and_fields_stripped(self):
        text = (
            "memo,category,currency,amount,date,id\n"
            "  a memo  ,  food ,  USD , -3.5 , 2026-03-07 ,  x1  \n"
        )
        (tx,) = parse_text(text)
        assert tx == Transaction(
            id="x1",
            date=datetime.date(2026, 3, 7),
            amount=Decimal("-3.5"),
            currency="USD",
            category="food",
            memo="a memo",
        )

    def test_extra_columns_ignored(self):
        text = "id,extra,date,amount,currency,category,memo\nt1,zzz,2026-03-01,1,ILS,food,\n"
        (tx,) = parse_text(text)
        assert tx.id == "t1"
        assert tx.category == "food"

    def test_header_only_returns_empty_list(self):
        assert parse_text(HEADER) == []

    def test_header_with_spaces_matches(self):
        text = " id , date , amount , currency , category , memo \n" + VALID_ROW
        assert len(parse_text(text)) == 1


class TestBomBlankQuoted:
    def test_fixture(self):
        txs = parse_csv(FIXTURES / "bom_blank.csv")
        assert [tx.id for tx in txs] == ["b1", "b2"]
        assert txs[0].memo == ""
        assert txs[1].memo == "flowers, card"

    def test_blank_lines_count_for_line_numbers(self):
        raw = (FIXTURES / "bom_blank.csv").read_text(encoding="utf-8-sig")
        raw = raw.replace("40,EUR", "40,GBP")
        assert error_of(raw).line == 7

    def test_bom_in_text_stream_is_ignored(self):
        assert len(parse_text("\ufeff" + HEADER + VALID_ROW)) == 1


BAD_ROWS = [
    ("t2,2026-3-1,1,ILS,food,", "date '2026-3-1' is not YYYY-MM-DD"),
    ("t2,2026-02-30,1,ILS,food,", "date '2026-02-30' is not a calendar date"),
    ("t2,2026-03-01,abc,ILS,food,", "amount 'abc' is not a number"),
    ("t2,2026-03-01,NaN,ILS,food,", "amount 'NaN' is not a number"),
    ("t2,2026-03-01,Infinity,ILS,food,", "amount 'Infinity' is not a number"),
    ("t2,2026-03-01,1.505,ILS,food,", "amount '1.505' has more than 2 decimal places"),
    ("t2,2026-03-01,0,ILS,food,", "amount must not be zero"),
    ("t2,2026-03-01,-0.00,ILS,food,", "amount must not be zero"),
    ("t2,2026-03-01,1,usd,food,", "unknown currency 'usd'"),
    ("t2,2026-03-01,1,ILS,,", "empty category"),
    (",2026-03-01,1,ILS,food,", "empty id"),
    ("t2,2026-03-01,1,ILS,food", "expected 6 fields, got 5"),
]


class TestRowErrors:
    @pytest.mark.parametrize("row,reason", BAD_ROWS)
    def test_reason_and_line(self, row, reason):
        err = error_of(HEADER + VALID_ROW + row + "\n")
        assert err.line == 3
        assert err.reason == reason
        assert str(err) == f"line 3: {reason}"

    def test_control_row_is_valid(self):
        assert len(parse_text(HEADER + VALID_ROW)) == 1

    def test_stops_at_first_bad_row(self):
        text = HEADER + "t1,2026-03-01,abc,ILS,food,\n" + "t2,bad,1,ILS,food,\n"
        assert error_of(text).line == 2

    def test_duplicate_id_across_blank_line(self):
        text = HEADER + "t1,2026-03-01,1,ILS,food,\n\nt1,2026-03-02,2,ILS,food,\n"
        err = error_of(text)
        assert err.line == 4
        assert err.reason == "duplicate id 't1' (first seen on line 2)"

    def test_multiline_quoted_memo_line_numbers(self):
        text = HEADER + 't1,2026-03-01,1,ILS,food,"two\nlines"\n' + "t2,2026-03-01,1,XXX,food,\n"
        err = error_of(text)
        assert err.line == 4

    def test_bad_amount_fixture_fails_on_line_3(self):
        with pytest.raises(LedgerError) as info:
            parse_csv(FIXTURES / "bad_amount.csv")
        assert info.value.line == 3
        assert info.value.reason == "amount '-2.505' has more than 2 decimal places"


class TestHeaderErrors:
    def test_missing_columns_in_canonical_order(self):
        err = error_of("memo,amount,id,date\n")
        assert err.line == 1
        assert err.reason == "missing column(s): currency, category"

    def test_missing_columns_story_example(self):
        err = error_of("id,date,amount\n")
        assert err.line == 1
        assert err.reason == "missing column(s): currency, category, memo"

    def test_empty_file(self):
        with pytest.raises(LedgerError) as info:
            parse_csv(FIXTURES / "empty.csv")
        assert info.value.line == 1
        assert info.value.reason == "missing header"

    def test_blank_only_text_is_missing_header(self):
        err = error_of("\n  \n")
        assert (err.line, err.reason) == (1, "missing header")


class TestEntryPoints:
    def test_parse_lines_matches_parse_csv(self):
        path = FIXTURES / "sample.csv"
        text = path.read_text(encoding="utf-8")
        assert parse_lines(io.StringIO(text)) == parse_csv(path)
        assert parse_lines(text.splitlines(keepends=True)) == parse_csv(path)

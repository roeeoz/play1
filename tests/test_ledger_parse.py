import datetime
import io
import pathlib
from decimal import Decimal

import pytest

from ledger import COLUMNS, CURRENCIES, LedgerError, Transaction, parse_csv, parse_lines

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "ledger"
HEADER = "id,date,amount,currency,category,memo\n"
VALID = "t0,2026-03-01,1.00,ILS,food,control\n"


def parse_text(text):
    return parse_lines(io.StringIO(text))


def error_of(text):
    with pytest.raises(LedgerError) as info:
        parse_text(text)
    return info.value


class TestModel:
    def test_currencies(self):
        assert CURRENCIES == ("ILS", "USD", "EUR")
        assert COLUMNS == ("id", "date", "amount", "currency", "category", "memo")

    def test_transaction_is_frozen(self):
        tx = Transaction("a", datetime.date(2026, 3, 1), Decimal("1"), "ILS", "c", "")
        with pytest.raises(AttributeError):
            tx.amount = Decimal("2")

    def test_ledger_error(self):
        err = LedgerError(4, "empty id")
        assert isinstance(err, Exception)
        assert err.line == 4
        assert err.reason == "empty id"
        assert str(err) == "line 4: empty id"


class TestHappyPath:
    def test_sample_file(self):
        txs = parse_csv(FIXTURES / "sample.csv")
        assert [t.id for t in txs] == [f"t00{i}" for i in range(1, 10)]
        first = txs[0]
        assert first == Transaction(
            "t001", datetime.date(2026, 3, 1), Decimal("12000.00"), "ILS", "salary",
            "March salary",
        )
        assert str(first.amount) == "12000.00"
        assert txs[6].memo == ""
        assert txs[2].currency == "USD" and txs[2].amount == Decimal("-120")
        assert sum(t.date.month == 3 for t in txs) == 7
        assert txs[7].date == datetime.date(2026, 2, 27)
        assert txs[8].date == datetime.date(2026, 4, 1)
        for t in txs:
            assert isinstance(t.date, datetime.date)
            assert isinstance(t.amount, Decimal)

    def test_header_order_free_and_fields_stripped(self):
        text = (
            "memo,category, currency ,amount,date,id,extra\n"
            "  a memo , food ,  USD , -3.5 , 2026-03-04 ,  x1  , ignored \n"
        )
        assert parse_text(text) == [
            Transaction("x1", datetime.date(2026, 3, 4), Decimal("-3.5"), "USD", "food",
                        "a memo")
        ]

    def test_bom_blank_lines_and_quoted_memo(self):
        txs = parse_csv(FIXTURES / "bom_blank.csv")
        assert [t.id for t in txs] == ["b1", "b2"]
        assert txs[0].memo == ""
        assert txs[1].memo == "novel, used"

    def test_header_only(self):
        assert parse_text(HEADER) == []

    def test_parse_lines_matches_parse_csv(self):
        path = FIXTURES / "sample.csv"
        text = path.read_text(encoding="utf-8")
        assert parse_lines(io.StringIO(text)) == parse_csv(path)
        assert parse_lines(text.splitlines(keepends=True)) == parse_csv(path)


class TestRowErrors:
    @pytest.mark.parametrize(
        "row, reason",
        [
            ("t1,2026-3-1,1,ILS,food,m", "date '2026-3-1' is not YYYY-MM-DD"),
            ("t1,2026-02-30,1,ILS,food,m", "date '2026-02-30' is not a calendar date"),
            ("t1,2026-03-01,abc,ILS,food,m", "amount 'abc' is not a number"),
            ("t1,2026-03-01,NaN,ILS,food,m", "amount 'NaN' is not a number"),
            ("t1,2026-03-01,Infinity,ILS,food,m", "amount 'Infinity' is not a number"),
            ("t1,2026-03-01,,ILS,food,m", "amount '' is not a number"),
            ("t1,2026-03-01,1.505,ILS,food,m", "amount '1.505' has more than 2 decimal places"),
            ("t1,2026-03-01,0,ILS,food,m", "amount must not be zero"),
            ("t1,2026-03-01,-0.00,ILS,food,m", "amount must not be zero"),
            ("t1,2026-03-01,1,usd,food,m", "unknown currency 'usd'"),
            ("t1,2026-03-01,1,ILS,,m", "empty category"),
            (",2026-03-01,1,ILS,food,m", "empty id"),
            ("t1,2026-03-01,1,ILS,food", "expected 6 fields, got 5"),
        ],
    )
    def test_reason(self, row, reason):
        err = error_of(HEADER + VALID + row + "\n" + "t9,2026-03-01,bad,ILS,x,\n")
        assert (err.line, err.reason) == (3, reason)
        assert str(err) == f"line 3: {reason}"

    def test_control_rows_parse(self):
        assert len(parse_text(HEADER + VALID + "t1,2026-03-01,1,ILS,food,m\n")) == 2

    def test_duplicate_id_across_blank_line(self):
        err = error_of(HEADER + "t1,2026-03-01,1,ILS,a,\n\nt1,2026-03-02,2,ILS,b,\n")
        assert err.line == 4
        assert err.reason == "duplicate id 't1' (first seen on line 2)"

    def test_line_numbers_count_blank_lines_and_multiline_fields(self):
        text = (
            "\n" + HEADER + "\n"
            't1,2026-03-01,1,ILS,a,"two\nlines"\n'
            "   \n"
            "t2,2026-03-01,1,EUR,,\n"
        )
        err = error_of(text)
        assert err.line == 7
        assert err.reason == "empty category"

    def test_bad_amount_fixture(self):
        with pytest.raises(LedgerError) as info:
            parse_csv(FIXTURES / "bad_amount.csv")
        assert info.value.line == 3
        assert info.value.reason == "amount '-2.505' has more than 2 decimal places"


class TestHeaderErrors:
    def test_missing_columns(self):
        err = error_of("memo,amount,date,id\n")
        assert (err.line, err.reason) == (1, "missing column(s): currency, category")

    def test_missing_columns_canonical_order(self):
        err = error_of("amount,date,id\n")
        assert (err.line, err.reason) == (1, "missing column(s): currency, category, memo")

    def test_empty_file(self):
        with pytest.raises(LedgerError) as info:
            parse_csv(FIXTURES / "empty.csv")
        assert (info.value.line, info.value.reason) == (1, "missing header")

    def test_blank_only_text_is_missing_header(self):
        err = error_of("\n  \n")
        assert (err.line, err.reason) == (1, "missing header")

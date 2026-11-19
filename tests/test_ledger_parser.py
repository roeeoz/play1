import dataclasses
import datetime
import io
import pathlib
from decimal import Decimal

import pytest

from ledger import LedgerError, Transaction, parse_csv, parse_lines

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "ledger"
HEADER = "id,date,amount,currency,category,memo\n"


def parse_text(text):
    return parse_lines(io.StringIO(text))


def error_of(text):
    with pytest.raises(LedgerError) as info:
        parse_text(text)
    return info.value


def row(id="t1", date="2026-03-01", amount="10.00", currency="ILS",
        category="food", memo="m"):
    return f"{id},{date},{amount},{currency},{category},{memo}\n"


class TestSample:
    def test_nine_transactions_in_file_order(self):
        txs = parse_csv(FIXTURES / "sample.csv")
        assert [t.id for t in txs] == [f"t00{i}" for i in range(1, 10)]
        assert all(isinstance(t, Transaction) for t in txs)
        months = [(t.date.year, t.date.month) for t in txs]
        assert months.count((2026, 3)) == 7
        assert txs[0].date == datetime.date(2026, 2, 27)
        assert txs[8].date == datetime.date(2026, 4, 1)

    def test_field_types_and_exact_amount(self):
        txs = parse_csv(str(FIXTURES / "sample.csv"))
        salary = txs[1]
        assert salary.amount == Decimal("12000.00")
        assert str(salary.amount) == "12000.00"
        for t in txs:
            assert isinstance(t.id, str)
            assert isinstance(t.date, datetime.date)
            assert isinstance(t.amount, Decimal)
            assert isinstance(t.currency, str)
            assert isinstance(t.category, str)
            assert isinstance(t.memo, str)
        assert any(t.memo == "" for t in txs)

    def test_transaction_is_frozen(self):
        t = parse_csv(FIXTURES / "sample.csv")[0]
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.amount = Decimal("1")


class TestHeader:
    def test_columns_matched_by_name_and_fields_trimmed(self):
        text = (
            " memo , category,currency,amount,date,id \n"
            "  hello  , food ,  USD ,  -3.50 , 2026-03-04 ,  a1  \n"
        )
        (t,) = parse_text(text)
        assert t == Transaction("a1", datetime.date(2026, 3, 4),
                                Decimal("-3.50"), "USD", "food", "hello")

    def test_extra_columns_ignored(self):
        text = "id,date,extra,amount,currency,category,memo\n" \
               "a1,2026-03-04,whatever,5,ILS,food,\n"
        (t,) = parse_text(text)
        assert t.amount == Decimal("5") and t.memo == ""

    def test_header_names_case_sensitive(self):
        e = error_of("ID,date,amount,currency,category,memo\n")
        assert (e.line, e.reason) == (1, "missing column(s): id")

    def test_duplicate_column(self):
        e = error_of("\nid,date,amount,currency,category,memo,id\n")
        assert (e.line, e.reason) == (2, "duplicate column 'id'")

    def test_missing_columns_in_canonical_order(self):
        e = error_of("memo,amount,date,id\n")
        assert (e.line, e.reason) == (1, "missing column(s): currency, category")
        e = error_of("amount,id,date\n")
        assert (e.line, e.reason) == (1, "missing column(s): currency, category, memo")
        assert str(e) == "line 1: missing column(s): currency, category, memo"

    def test_header_only_returns_empty_list(self):
        assert parse_text(HEADER) == []
        assert parse_text(HEADER.rstrip("\n")) == []

    def test_empty_file_missing_header(self):
        path = FIXTURES / "empty.csv"
        assert path.read_bytes() == b""
        with pytest.raises(LedgerError) as info:
            parse_csv(path)
        assert (info.value.line, info.value.reason) == (1, "missing header")

    def test_only_blank_lines_missing_header(self):
        e = error_of("\n   \n\n")
        assert (e.line, e.reason) == (1, "missing header")


class TestBomBlank:
    def test_fixture_starts_with_bom(self):
        assert (FIXTURES / "bom_blank.csv").read_bytes().startswith(b"\xef\xbb\xbf")

    def test_parses_two_transactions(self):
        txs = parse_csv(FIXTURES / "bom_blank.csv")
        assert [t.id for t in txs] == ["b1", "b2"]
        assert txs[0].memo == ""
        assert txs[1].memo == "from Dana, thanks"

    def test_line_numbers_count_blank_lines(self):
        content = (FIXTURES / "bom_blank.csv").read_text(encoding="utf-8-sig")
        content = content.replace("b2,", "b1,")
        e = error_of(content)
        assert (e.line, e.reason) == (5, "duplicate id 'b1' (first seen on line 2)")


class TestRowErrors:
    @pytest.mark.parametrize(
        "kwargs, reason",
        [
            ({"date": "2026-3-1"}, "date '2026-3-1' is not YYYY-MM-DD"),
            ({"date": "20260301"}, "date '20260301' is not YYYY-MM-DD"),
            ({"date": "２０２６-03-01"}, "date '２０２６-03-01' is not YYYY-MM-DD"),
            ({"date": "2026-02-30"}, "date '2026-02-30' is not a calendar date"),
            ({"date": "2026-13-01"}, "date '2026-13-01' is not a calendar date"),
            ({"amount": "abc"}, "amount 'abc' is not a number"),
            ({"amount": "NaN"}, "amount 'NaN' is not a number"),
            ({"amount": "Infinity"}, "amount 'Infinity' is not a number"),
            ({"amount": "1e3"}, "amount '1e3' is not a number"),
            ({"amount": "1_000"}, "amount '1_000' is not a number"),
            ({"amount": ".5"}, "amount '.5' is not a number"),
            ({"amount": "5."}, "amount '5.' is not a number"),
            ({"amount": "٣"}, "amount '٣' is not a number"),
            ({"amount": ""}, "amount '' is not a number"),
            ({"amount": "1.505"}, "amount '1.505' has more than 2 decimal places"),
            ({"amount": "1.500"}, "amount '1.500' has more than 2 decimal places"),
            ({"amount": "0"}, "amount must not be zero"),
            ({"amount": "0.00"}, "amount must not be zero"),
            ({"amount": "-0.00"}, "amount must not be zero"),
            ({"amount": "+0.0"}, "amount must not be zero"),
            ({"currency": "usd"}, "unknown currency 'usd'"),
            ({"currency": "GBP"}, "unknown currency 'GBP'"),
            ({"category": "  "}, "empty category"),
            ({"id": ""}, "empty id"),
        ],
    )
    def test_reason(self, kwargs, reason):
        e = error_of(HEADER + row(id="ok") + row(**kwargs))
        assert (e.line, e.reason) == (3, reason)
        assert str(e) == f"line 3: {reason}"

    def test_field_count(self):
        e = error_of(HEADER + "t1,2026-03-01,10,ILS,food\n")
        assert (e.line, e.reason) == (2, "expected 6 fields, got 5")

    def test_field_count_uses_header_width(self):
        e = error_of("id,date,amount,currency,category,memo,x\n" + row())
        assert e.reason == "expected 7 fields, got 6"

    def test_row_of_commas_is_empty_id(self):
        assert error_of(HEADER + ",,,,,\n").reason == "empty id"

    def test_duplicate_id_with_blank_line_between(self):
        e = error_of(HEADER + row() + "\n" + row())
        assert (e.line, e.reason) == (4, "duplicate id 't1' (first seen on line 2)")

    def test_plus_amount_accepted(self):
        (t,) = parse_text(HEADER + row(amount="+5"))
        assert t.amount == Decimal("5")

    def test_stops_at_first_bad_row(self):
        e = error_of(HEADER + row(amount="x") + row(id="t2", currency="usd"))
        assert e.line == 2 and e.reason == "amount 'x' is not a number"

    @pytest.mark.parametrize(
        "kwargs, reason",
        [
            ({"id": "", "date": "bad"}, "empty id"),
            ({"id": "t0", "date": "bad"}, "duplicate id 't0' (first seen on line 2)"),
            ({"date": "bad", "amount": "x"}, "date 'bad' is not YYYY-MM-DD"),
            ({"amount": "x", "currency": "x"}, "amount 'x' is not a number"),
            ({"currency": "x", "category": ""}, "unknown currency 'x'"),
        ],
    )
    def test_check_order(self, kwargs, reason):
        assert error_of(HEADER + row(id="t0") + row(**kwargs)).reason == reason

    def test_field_count_checked_first(self):
        e = error_of(HEADER + ",bad,x,y\n")
        assert e.reason == "expected 6 fields, got 4"

    def test_multiline_quoted_field_counts_lines(self):
        text = HEADER + 't1,2026-03-01,1,ILS,food,"two\nlines"\n' + row(id="t2", amount="x")
        e = error_of(text)
        assert e.line == 4
        (t,) = parse_text(HEADER + 't1,2026-03-01,1,ILS,food,"two\nlines"\n')
        assert t.memo == "two\nlines"

    def test_malformed_csv(self):
        e = error_of(HEADER + row() + 't2,2026-03-01,1,ILS,food,"unterminated\n')
        assert e.line == 3
        assert e.reason.startswith("malformed CSV: ")

    def test_bad_amount_fixture(self):
        with pytest.raises(LedgerError) as info:
            parse_csv(FIXTURES / "bad_amount.csv")
        assert info.value.line == 3
        assert info.value.reason == "amount '-2.505' has more than 2 decimal places"


class TestEntryPoints:
    def test_parse_lines_inputs_match_parse_csv(self):
        path = FIXTURES / "sample.csv"
        expected = parse_csv(path)
        text = path.read_text(encoding="utf-8")
        assert parse_lines(io.StringIO(text)) == expected
        assert parse_lines(text.splitlines(keepends=True)) == expected
        assert parse_lines(text.splitlines()) == expected
        assert parse_lines(io.StringIO("\ufeff" + text)) == expected

    def test_parse_lines_bom_matches_bom_fixture(self):
        raw = (FIXTURES / "bom_blank.csv").read_bytes().decode("utf-8")
        assert raw.startswith("\ufeff")
        assert parse_lines(io.StringIO(raw, newline="")) == parse_csv(FIXTURES / "bom_blank.csv")

    def test_same_error_from_both(self):
        path = FIXTURES / "bad_amount.csv"
        with pytest.raises(LedgerError) as from_file:
            parse_csv(path)
        with pytest.raises(LedgerError) as from_lines:
            parse_lines(path.read_text(encoding="utf-8").splitlines())
        assert str(from_file.value) == str(from_lines.value)

    def test_missing_file_raises_oserror(self, tmp_path):
        with pytest.raises(OSError):
            parse_csv(tmp_path / "nope.csv")

    def test_invalid_utf8_raises_unicode_error(self, tmp_path):
        path = tmp_path / "bad.csv"
        path.write_bytes(HEADER.encode() + b"t1,2026-03-01,1,ILS,\xff\xfe,m\n")
        with pytest.raises(UnicodeDecodeError):
            parse_csv(path)

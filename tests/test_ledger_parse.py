"""Tests for the ``ledger`` package: CSV parsing and validation (FIPSPROBE-2)."""

import io
import pickle
from datetime import date
from decimal import Decimal

import pytest

import ledger
from ledger import LedgerError, LedgerReadError, Transaction, parse_csv, parse_lines

HEADER = "id,date,amount,currency,category,memo"


def row(id="T-1", date="2026-03-01", amount="10.00", currency="ILS", category="food", memo="m"):
    return f"{id},{date},{amount},{currency},{category},{memo}"


def error_of(lines):
    with pytest.raises(LedgerError) as info:
        parse_lines(lines)
    return info.value.line, info.value.reason


def write(tmp_path, content, name="ledger.csv"):
    path = tmp_path / name
    path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
    return path


def physical_lines(content):
    """Split like a file read with newline='' does, keeping the endings."""
    return list(io.StringIO(content, newline=""))


def outcome(fn, arg):
    try:
        return fn(arg)
    except LedgerError as exc:
        return (exc.line, exc.reason)


def test_public_surface():
    assert set(ledger.__all__) == {
        "parse_csv", "parse_lines", "Transaction", "LedgerError", "LedgerReadError",
    }


class TestHappyPath:
    CONTENT = (
        "\ufeff" + HEADER + "\r\n"
        "T-1,2026-03-01,-12.50,ILS,food,\"bread, milk\"\r\n"
        "\r\n"
        "T-2,2026-03-02,+3,USD,fun,\"the \"\"big\"\" show\"\r\n"
        "T-3,2026-03-03,0,EUR,misc,\"line one\r\nline two\"\r\n"
        "T-4,2026-04-01,7.5,ILS,salary,\r\n"
    )

    def test_rows_in_file_order_with_exact_decimals(self, tmp_path):
        txs = parse_csv(write(tmp_path, self.CONTENT))
        assert [t.id for t in txs] == ["T-1", "T-2", "T-3", "T-4"]
        assert [t.amount for t in txs] == [
            Decimal("-12.50"), Decimal("3"), Decimal("0"), Decimal("7.5"),
        ]
        assert all(type(t.amount) is Decimal for t in txs)
        assert str(txs[0].amount) == "-12.50"
        assert txs[0].memo == "bread, milk"
        assert txs[1].memo == 'the "big" show'
        assert txs[2].memo == "line one\r\nline two"
        assert txs[3].memo == ""
        assert txs[0] == Transaction("T-1", date(2026, 3, 1), Decimal("-12.50"), "ILS", "food", "bread, milk")

    def test_negative_amount_is_expense(self):
        (t,) = parse_lines([HEADER, row(amount="-12.50")])
        assert t.amount < 0

    def test_transaction_is_frozen(self):
        (t,) = parse_lines([HEADER, row()])
        with pytest.raises(AttributeError):
            t.amount = Decimal("1")

    def test_reordered_header_with_extra_column(self):
        txs = parse_lines([
            "memo, category ,extra,currency,amount,date,id",
            "hello,food,ignored,USD,4.20,2026-03-05,A1",
        ])
        assert txs == [Transaction("A1", date(2026, 3, 5), Decimal("4.20"), "USD", "food", "hello")]
        assert not hasattr(txs[0], "extra")

    def test_repeated_parse_is_independent(self):
        lines = [HEADER, row()]
        assert parse_lines(lines) == parse_lines(lines)


class TestHeader:
    @pytest.mark.parametrize("header", [
        "id,date,amount,currency,category",
        "id,date,amount,currency,category,Memo",
    ])
    def test_missing_memo(self, header):
        assert error_of([header, "x,y,z,a,b,c"]) == (1, "missing column 'memo'")

    def test_duplicate_id_column(self):
        assert error_of(["id,date,amount,currency,category,memo,id"]) == (1, "duplicate column 'id'")

    def test_missing_checked_before_duplicate(self):
        assert error_of(["id,id,amount,currency,category,memo"]) == (1, "missing column 'date'")

    @pytest.mark.parametrize("lines", [[], [""], ["", "   ", "\n"]])
    def test_missing_header(self, lines):
        assert error_of(lines) == (1, "missing header")

    def test_missing_header_from_empty_file(self, tmp_path):
        with pytest.raises(LedgerError) as info:
            parse_csv(write(tmp_path, ""))
        assert (info.value.line, info.value.reason) == (1, "missing header")

    def test_header_after_blank_lines_reports_line_1(self):
        assert error_of(["", "", "id,date"]) == (1, "missing column 'amount'")


class TestRows:
    def test_wrong_field_count(self):
        assert error_of([HEADER, row(), "T-2,2026-03-01,1,ILS,food"]) == (3, "row has 5 fields, expected 6")

    @pytest.mark.parametrize("value", ["", "   "])
    def test_empty_id(self, value):
        assert error_of([HEADER, row(id=value)]) == (2, "empty id")

    def test_duplicate_id(self):
        lines = [HEADER, row("A"), row("B"), row("T-7"), row("C"), row("D"), row("E"), row("F"), row("T-7")]
        assert error_of(lines) == (9, "duplicate id 'T-7' (first seen on line 4)")

    def test_ids_are_case_sensitive(self):
        assert [t.id for t in parse_lines([HEADER, row("T-7"), row("t-7")])] == ["T-7", "t-7"]

    @pytest.mark.parametrize("value", ["2026-13-01", "2026-02-30", "01/03/2026", "20260301", "2026-3-01", "\uff12\uff10\uff12\uff16-03-01"])
    def test_invalid_date(self, value):
        assert error_of([HEADER, row(date=value)]) == (2, f"invalid date '{value}'")

    def test_valid_date(self):
        (t,) = parse_lines([HEADER, row(date="2024-02-29")])
        assert t.date == date(2024, 2, 29) and type(t.date) is date

    @pytest.mark.parametrize("value", ["abc", "1,000.00", "12.", ".5", "1e3", "NaN", "1_000", "\u0661\u0662", "", "Infinity", "--1"])
    def test_amount_not_a_number(self, value):
        line = HEADER, row(amount=f'"{value}"')
        assert error_of(list(line)) == (2, f"amount '{value}' is not a number")

    def test_too_many_decimals_on_line_17(self):
        lines = [HEADER] + [row(id=f"T-{i}") for i in range(2, 17)] + [row(id="X", amount="12.345")]
        assert error_of(lines) == (17, "amount '12.345' has more than 2 decimal places")

    @pytest.mark.parametrize("value, expected", [("-12.50", "-12.50"), ("+3", "3"), ("0", "0"), ("7.5", "7.5")])
    def test_accepted_amounts(self, value, expected):
        (t,) = parse_lines([HEADER, row(amount=value)])
        assert type(t.amount) is Decimal
        assert t.amount == Decimal(value)
        assert str(t.amount) == expected

    def test_currencies(self):
        txs = parse_lines([HEADER, row("a", currency="ILS"), row("b", currency="USD"), row("c", currency="EUR")])
        assert [t.currency for t in txs] == ["ILS", "USD", "EUR"]

    @pytest.mark.parametrize("value", ["usd", "Eur", "GBP"])
    def test_unknown_currency(self, value):
        assert error_of([HEADER, row(currency=value)]) == (2, f"unknown currency '{value}'")

    def test_empty_category(self):
        assert error_of([HEADER, row(category=" ")]) == (2, "empty category")

    def test_empty_memo(self):
        (t,) = parse_lines([HEADER, row(memo="")])
        assert t.memo == ""

    def test_fields_are_trimmed(self):
        (t,) = parse_lines([HEADER, " T-1 , 2026-03-01 , 5.00 , USD , food ,  hi  "])
        assert t == Transaction("T-1", date(2026, 3, 1), Decimal("5.00"), "USD", "food", "hi")

    def test_error_reports_trimmed_value(self):
        assert error_of([HEADER, row(currency=" usd ")]) == (2, "unknown currency 'usd'")


class TestValidationOrder:
    def test_field_count_first(self):
        assert error_of([HEADER, ",bad,abc,usd,"]) == (2, "row has 5 fields, expected 6")

    def test_empty_id_before_date(self):
        assert error_of([HEADER, ",bad,abc,usd,,"]) == (2, "empty id")

    def test_duplicate_id_before_date(self):
        assert error_of([HEADER, row("A"), "A,bad,abc,usd,,"]) == (3, "duplicate id 'A' (first seen on line 2)")

    def test_date_before_amount(self):
        assert error_of([HEADER, "A,bad,abc,usd,,"]) == (2, "invalid date 'bad'")

    def test_amount_before_currency(self):
        assert error_of([HEADER, "A,2026-03-01,abc,usd,,"]) == (2, "amount 'abc' is not a number")

    def test_currency_before_category(self):
        assert error_of([HEADER, "A,2026-03-01,1.234,usd,,"]) == (2, "amount '1.234' has more than 2 decimal places")
        assert error_of([HEADER, "A,2026-03-01,1,usd,,"]) == (2, "unknown currency 'usd'")


class TestLineNumbers:
    def test_blank_lines_count(self):
        assert error_of([HEADER, "", "", row(currency="x")]) == (4, "unknown currency 'x'")

    def test_multiline_record_reported_at_first_line(self):
        lines = [HEADER, row("A"), row("B"), row("C"), 'D,2026-03-01,1,xx,food,"spans', 'two lines"']
        assert error_of(lines) == (5, "unknown currency 'xx'")

    def test_line_after_multiline_record(self):
        lines = [HEADER, 'A,2026-03-01,1,ILS,food,"a', 'b"', row("B", currency="x")]
        assert error_of(lines) == (4, "unknown currency 'x'")

    def test_whitespace_only_line_is_blank(self):
        assert len(parse_lines([HEADER, "   \t ", row()])) == 1

    def test_commas_only_line_is_empty_id(self):
        assert error_of([HEADER, ",,,,,"]) == (2, "empty id")


class TestMalformedCsv:
    def test_unclosed_quote(self):
        assert error_of([HEADER, row("A"), 'B,2026-03-01,1,ILS,food,"never closed', "more"]) == (3, "malformed CSV record")

    def test_text_after_closing_quote(self):
        assert error_of([HEADER, 'a,"b"c,1,ILS,food,m']) == (2, "malformed CSV record")

    def test_malformed_from_file(self, tmp_path):
        with pytest.raises(LedgerError) as info:
            parse_csv(write(tmp_path, HEADER + '\nA,2026-03-01,1,ILS,food,"open\n'))
        assert (info.value.line, info.value.reason) == (2, "malformed CSV record")


class TestErrorShape:
    def test_line_reason_and_text(self):
        with pytest.raises(LedgerError) as info:
            parse_lines([HEADER, row(amount="12.345")])
        err = info.value
        assert err.line == 2
        assert err.reason == "amount '12.345' has more than 2 decimal places"
        assert str(err) == "2: amount '12.345' has more than 2 decimal places"
        assert err.args == (str(err),)

    def test_error_round_trips_through_pickle(self):
        err = pickle.loads(pickle.dumps(LedgerError(3, "empty id")))
        assert (err.line, err.reason, str(err)) == (3, "empty id", "3: empty id")

    def test_no_transactions_on_error(self):
        result = None
        with pytest.raises(LedgerError):
            result = parse_lines([HEADER, row("A"), row("B", currency="x")])
        assert result is None


class TestUnreadableFile:
    def test_missing_file(self, tmp_path):
        with pytest.raises(LedgerReadError) as info:
            parse_csv(tmp_path / "nope.csv")
        assert not isinstance(info.value, LedgerError)
        assert isinstance(info.value.__cause__, OSError)

    def test_invalid_utf8_wins_over_earlier_data_error(self, tmp_path):
        content = (HEADER + "\nA,2026-03-01,1,usd,food,\nB,2026-03-01,1,ILS,food,\xff\n").encode("latin-1")
        with pytest.raises(LedgerReadError) as info:
            parse_csv(write(tmp_path, content))
        assert not isinstance(info.value, LedgerError)
        assert isinstance(info.value.__cause__, UnicodeDecodeError)

    def test_accepts_str_path(self, tmp_path):
        assert len(parse_csv(str(write(tmp_path, HEADER + "\n" + row())))) == 1


class TestParity:
    CASES = {
        "bom": "\ufeff" + HEADER + "\r\n" + row("A") + "\r\n\r\n" + row("B") + "\r\n",
        "multiline memo": HEADER + "\n" + 'A,2026-03-01,1,ILS,food,"one\ntwo"\n' + row("B") + "\n",
        "unicode separator in memo": HEADER + "\n" + 'A,2026-03-01,1,ILS,food,"x\u2028y"\n' + row("B", currency="x") + "\n",
        "error after multiline": "\ufeff" + HEADER + "\n\n" + 'A,2026-03-01,1,ILS,food,"one\ntwo"\n' + row("A") + "\n",
        "no trailing newline": HEADER + "\n" + row("A"),
    }

    @pytest.mark.parametrize("name", list(CASES))
    def test_file_and_lines_agree(self, tmp_path, name):
        content = self.CASES[name]
        from_file = outcome(parse_csv, write(tmp_path, content))
        with_endings = physical_lines(content)
        without_endings = [line.rstrip("\r\n") for line in with_endings]
        assert outcome(parse_lines, with_endings) == from_file
        assert outcome(parse_lines, without_endings) == from_file

    def test_unicode_separator_is_not_a_line_break(self, tmp_path):
        assert outcome(parse_csv, write(tmp_path, self.CASES["unicode separator in memo"])) == (3, "unknown currency 'x'")

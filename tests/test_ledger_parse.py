import dataclasses
import datetime
from decimal import Decimal

import pytest

import ledger
from ledger import LedgerError, Transaction, parse_csv, parse_lines

HEADER = "id,date,amount,currency,category,memo\n"
BOM = "\ufeff"


def lines_of(text):
    return text.splitlines(keepends=True)


def parse_text(text):
    return parse_lines(lines_of(text))


def error_of(text):
    with pytest.raises(LedgerError) as info:
        parse_text(text)
    return info.value


def write(tmp_path, text, name="ledger.csv"):
    path = tmp_path / name
    path.write_bytes(text.encode("utf-8"))
    return path


def row(id="T-1", date="2026-03-01", amount="10.00", currency="ILS", category="food", memo="m"):
    return f"{id},{date},{amount},{currency},{category},{memo}\n"


HAPPY = (
    BOM
    + HEADER
    + row("T-1", "2026-03-01", "-12.50", "ILS", "food", "lunch")
    + "\n"
    + 'T-2,2026-03-02,1.10,USD,"rent, flat","said ""hi"""\n'
    + 'T-3,2026-03-03,0,EUR,misc,"two\nlines"\n'
    + row("T-4", "2026-04-30", "2500", "ILS", "salary", "")
)

HAPPY_EXPECTED = [
    Transaction("T-1", datetime.date(2026, 3, 1), Decimal("-12.50"), "ILS", "food", "lunch"),
    Transaction("T-2", datetime.date(2026, 3, 2), Decimal("1.10"), "USD", "rent, flat", 'said "hi"'),
    Transaction("T-3", datetime.date(2026, 3, 3), Decimal("0"), "EUR", "misc", "two\nlines"),
    Transaction("T-4", datetime.date(2026, 4, 30), Decimal("2500"), "ILS", "salary", ""),
]


class TestPublicSurface:
    def test_exports(self):
        assert set(ledger.__all__) == {"Transaction", "LedgerError", "parse_csv", "parse_lines"}

    def test_error_carries_line_and_reason(self):
        err = LedgerError(17, "missing id")
        assert err.line == 17
        assert err.reason == "missing id"
        assert str(err) == "17: missing id"

    def test_error_is_not_value_error(self):
        assert not isinstance(LedgerError(1, "missing header"), ValueError)
        assert isinstance(LedgerError(1, "missing header"), Exception)

    def test_transaction_is_frozen(self):
        tx = HAPPY_EXPECTED[0]
        with pytest.raises(dataclasses.FrozenInstanceError):
            tx.amount = Decimal("1")


class TestHappyPath:
    def test_in_memory(self):
        assert parse_text(HAPPY) == HAPPY_EXPECTED

    def test_file(self, tmp_path):
        assert parse_csv(write(tmp_path, HAPPY)) == HAPPY_EXPECTED

    def test_exact_types(self, tmp_path):
        for tx in parse_csv(write(tmp_path, HAPPY)):
            assert type(tx.amount) is Decimal
            assert type(tx.date) is datetime.date
            assert not any(isinstance(getattr(tx, f.name), float) for f in dataclasses.fields(tx))
        assert str(parse_text(HAPPY)[1].amount) == "1.10"

    def test_header_only(self):
        assert parse_text(HEADER) == []

    def test_columns_in_any_order_and_extra_columns(self):
        text = "memo,,category,x,currency,amount,x,date,id,\n" "hi,a,food,b,EUR,-3.5,c,2026-03-09,T-9,\n"
        assert parse_text(text) == [
            Transaction("T-9", datetime.date(2026, 3, 9), Decimal("-3.5"), "EUR", "food", "hi")
        ]

    def test_signs_kept(self):
        text = HEADER + row("A", amount="-1") + row("B", amount="2.5") + row("C", amount="0.00") + row("D", amount="-0")
        amounts = [tx.amount for tx in parse_text(text)]
        assert amounts == [Decimal("-1"), Decimal("2.5"), Decimal("0.00"), Decimal("-0")]
        assert amounts[0] < 0 < amounts[1]

    def test_values_not_trimmed(self):
        tx = parse_text(HEADER + row(id=" T-1", category="food ", memo=" m "))[0]
        assert (tx.id, tx.category, tx.memo) == (" T-1", "food ", " m ")


class TestHeaderErrors:
    @pytest.mark.parametrize("text", ["", "\n", "\n\n\n"])
    def test_missing_header(self, text):
        err = error_of(text)
        assert (err.line, err.reason) == (1, "missing header")

    def test_missing_header_file(self, tmp_path):
        with pytest.raises(LedgerError) as info:
            parse_csv(write(tmp_path, ""))
        assert str(info.value) == "1: missing header"

    def test_missing_column(self):
        err = error_of("\n\nid,amount,currency,category,memo\n")
        assert (err.line, err.reason) == (3, "missing column 'date'")

    def test_first_missing_in_catalogue_order(self):
        err = error_of("id,amount,category\n")
        assert err.reason == "missing column 'date'"

    def test_names_are_case_sensitive_and_untrimmed(self):
        assert error_of("id,Date,amount,currency,category,memo\n").reason == "missing column 'date'"
        assert error_of("id, date,amount,currency,category,memo\n").reason == "missing column 'date'"

    def test_duplicate_column(self):
        err = error_of("\nid,date,amount,currency,amount,category,memo\n")
        assert (err.line, err.reason) == (2, "duplicate column 'amount'")

    def test_missing_reported_before_duplicate(self):
        assert error_of("id,amount,amount,currency,category,memo\n").reason == "missing column 'date'"


class TestRowErrors:
    @pytest.mark.parametrize(
        "data_row, reason",
        [
            ("T-1,2026-03-01,1.00,ILS,food\n", "expected 6 fields, got 5"),
            ("T-1,2026-03-01,1.00,ILS,food,m,extra\n", "expected 6 fields, got 7"),
            ("   \n", "expected 6 fields, got 1"),
            (row(id=""), "missing id"),
            (row(date=""), "missing date"),
            (row(amount=""), "missing amount"),
            (row(currency=""), "missing currency"),
            (row(category=""), "missing category"),
            (row(date="2026-02-30"), "invalid date '2026-02-30'"),
            (row(date="20260301"), "invalid date '20260301'"),
            (row(date="2026-W10-1"), "invalid date '2026-W10-1'"),
            (row(date="2026-3-01"), "invalid date '2026-3-01'"),
            (row(date="٢٠٢٦-٠٣-٠١"), "invalid date '٢٠٢٦-٠٣-٠١'"),
            ('T-1,2026-03-01,"1,200.00",ILS,food,m\n', "invalid amount '1,200.00'"),
            (row(amount=" 12.00"), "invalid amount ' 12.00'"),
            (row(amount="1e2"), "invalid amount '1e2'"),
            (row(amount="NaN"), "invalid amount 'NaN'"),
            (row(amount="Infinity"), "invalid amount 'Infinity'"),
            (row(amount="1_000"), "invalid amount '1_000'"),
            (row(amount="+5"), "invalid amount '+5'"),
            (row(amount=".5"), "invalid amount '.5'"),
            (row(amount="5."), "invalid amount '5.'"),
            (row(amount="١٢"), "invalid amount '١٢'"),
            (row(amount="$5"), "invalid amount '$5'"),
            (row(amount="12.345"), "amount '12.345' has more than 2 decimal places"),
            (row(amount="12.3400"), "amount '12.3400' has more than 2 decimal places"),
            (row(currency="usd"), "unknown currency 'usd'"),
            (row(currency="GBP"), "unknown currency 'GBP'"),
            (row(currency="ILS "), "unknown currency 'ILS '"),
            (row(amount="1'2"), "invalid amount '1'2'"),
        ],
    )
    def test_reason(self, data_row, reason):
        err = error_of(HEADER + row("T-0") + data_row)
        assert (err.line, err.reason) == (3, reason)

    def test_decimals_on_line_17(self):
        rows = "".join(row(f"T-{n}") for n in range(15))
        err = error_of(HEADER + rows + row("T-99", amount="12.345"))
        assert (err.line, err.reason) == (17, "amount '12.345' has more than 2 decimal places")

    def test_duplicate_id(self):
        text = HEADER + row("A") + "\n" + row("T-7") + row("B") + row("C") + "\n" + row("D") + row("T-7")
        err = error_of(text)
        assert (err.line, err.reason) == (9, "duplicate id 'T-7' (first seen on line 4)")

    def test_duplicate_id_is_exact(self):
        assert len(parse_text(HEADER + row("T-7") + row("t-7") + row("T-7 "))) == 3

    def test_unknown_currency_stops_at_row(self):
        err = error_of(HEADER + row("A") + row("B", currency="usd") + row("C", amount="bad"))
        assert str(err) == "3: unknown currency 'usd'"

    def test_no_partial_result(self):
        # parse_lines either returns the full list or raises; nothing else escapes.
        with pytest.raises(LedgerError):
            parse_text(HEADER + row("A") + row("B", amount="x"))


class TestCheckOrder:
    @pytest.mark.parametrize(
        "data_row, reason",
        [
            ("T-1,2026-02-30,bad,usd,\n", "expected 6 fields, got 5"),
            (row(id="", date="bad", amount="bad"), "missing id"),
            (row(date="", amount="bad"), "missing date"),
            (row(date="2026-02-30", amount="bad", currency="usd"), "invalid date '2026-02-30'"),
            (row(amount="1.234", currency="usd"), "amount '1.234' has more than 2 decimal places"),
            (row("T-0", currency="usd"), "unknown currency 'usd'"),
        ],
    )
    def test_first_fault_wins(self, data_row, reason):
        assert error_of(HEADER + row("T-0") + data_row).reason == reason


class TestLineNumbers:
    def test_counts_bom_header_and_blank_lines(self):
        err = error_of(BOM + HEADER + "\n" + row("A") + "\n\n" + row("B", amount="x"))
        assert err.line == 6

    def test_multi_line_row_reports_start_line(self):
        text = HEADER + row("A") + "\n" + row("B") + 'C,2026-03-01,1.234,ILS,food,"spans\nlines"\n'
        err = error_of(text)
        assert (err.line, err.reason) == (5, "amount '1.234' has more than 2 decimal places")

    def test_row_after_multi_line_row(self):
        text = HEADER + 'A,2026-03-01,1,ILS,food,"a\nb\nc"\n' + row("B", currency="usd")
        assert error_of(text).line == 5

    def test_unterminated_quote_over_field_limit(self, tmp_path):
        filler = "x" * 1000 + "\n"
        text = HEADER + row("A") + 'B,2026-03-01,1,ILS,"food,never closed\n' + filler * 140
        assert len(text) > 131072
        with pytest.raises(LedgerError) as info:
            parse_csv(write(tmp_path, text))
        assert (info.value.line, info.value.reason) == (3, "expected 6 fields, got 5")


class TestFileEntryPoint:
    CASES = [
        HAPPY,
        HEADER,
        "",
        BOM + "\n" + HEADER + "\n" + row("A") + 'B,2026-03-01,1,ILS,food,"x\ny"\n' + row("C", amount="1e2"),
        BOM + HEADER + row("T-7") + "\n" + row("T-7"),
        BOM + "id,amount,currency,category,memo\n",
    ]

    @staticmethod
    def outcome(call):
        try:
            return call()
        except LedgerError as err:
            return (err.line, err.reason)

    @pytest.mark.parametrize("text", CASES)
    @pytest.mark.parametrize("newline", ["\n", "\r\n"])
    def test_same_as_in_memory(self, tmp_path, text, newline):
        content = text.replace("\n", newline)
        path = write(tmp_path, content)
        from_file = self.outcome(lambda: parse_csv(path))
        in_memory = self.outcome(lambda: parse_lines(content.splitlines(keepends=True)))
        assert from_file == in_memory

    def test_str_and_path(self, tmp_path):
        path = write(tmp_path, HAPPY)
        assert parse_csv(str(path)) == parse_csv(path) == HAPPY_EXPECTED

    def test_in_memory_bom_line_counts(self):
        assert error_of(BOM + HEADER + row(amount="x")).line == 2

    def test_missing_file_raises_os_error(self, tmp_path):
        with pytest.raises(FileNotFoundError) as info:
            parse_csv(tmp_path / "nope.csv")
        assert not isinstance(info.value, LedgerError)

    def test_directory_raises_os_error(self, tmp_path):
        with pytest.raises(OSError) as info:
            parse_csv(tmp_path)
        assert not isinstance(info.value, LedgerError)

    def test_invalid_utf8_raises_decode_error(self, tmp_path):
        path = tmp_path / "bad.csv"
        path.write_bytes(HEADER.encode() + b"T-1,2026-03-01,1,ILS,food,\xff\n")
        with pytest.raises(UnicodeDecodeError):
            parse_csv(path)

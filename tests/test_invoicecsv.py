import csv
import doctest
import inspect
import io
from datetime import date, datetime
from decimal import Decimal

import pytest

import testbed_utils
from testbed_utils import invoicecsv
from testbed_utils.invoicecsv import invoices_to_csv

HEADER = "number,customer,date,amount,status"


def _invoice(**overrides):
    invoice = {
        "number": "INV-001",
        "customer": "Acme",
        "date": date(2026, 3, 1),
        "amount": Decimal("1250.5"),
        "status": "paid",
    }
    invoice.update(overrides)
    return invoice


def _field(out, index):
    return out.splitlines()[1].split(",")[index]


class TestHeader:
    def test_first_line_is_exact_header(self):
        out = invoices_to_csv([_invoice(), _invoice(), _invoice()])
        assert out.split("\n")[0] == HEADER


class TestRows:
    def test_three_invoices_in_input_order(self):
        invoices = [
            _invoice(),
            _invoice(
                number="INV-002",
                customer="Bluefin",
                date=date(2026, 3, 14),
                amount=Decimal("980"),
                status="open",
            ),
            _invoice(
                number="INV-003",
                customer="Cobalt",
                date=date(2026, 3, 31),
                amount=Decimal("20"),
                status="overdue",
            ),
        ]
        assert invoices_to_csv(invoices) == (
            HEADER + "\n"
            "INV-001,Acme,2026-03-01,1250.50,paid\n"
            "INV-002,Bluefin,2026-03-14,980.00,open\n"
            "INV-003,Cobalt,2026-03-31,20.00,overdue\n"
        )

    def test_every_line_ends_with_newline(self):
        out = invoices_to_csv([_invoice()])
        assert out.endswith("\n")
        assert out.count("\n") == 2

    def test_utf8_round_trip_with_non_ascii_customer(self):
        out = invoices_to_csv([_invoice(customer="Zoë & Søn")])
        assert out.encode("utf-8").decode("utf-8") == out
        assert "Zoë & Søn" in out


class TestEmptyList:
    def test_header_only(self):
        assert invoices_to_csv([]) == HEADER + "\n"


class TestQuoting:
    def test_comma_in_customer_is_quoted(self):
        out = invoices_to_csv([_invoice(customer="Acme, Inc.")])
        assert out.splitlines()[1] == 'INV-001,"Acme, Inc.",2026-03-01,1250.50,paid'

    def test_reparsed_row_has_exactly_five_fields(self):
        out = invoices_to_csv([_invoice(customer="Acme, Inc.")])
        rows = list(csv.reader(io.StringIO(out)))
        assert len(rows) == 2
        assert [len(row) for row in rows] == [5, 5]
        assert rows[1][1] == "Acme, Inc."

    def test_embedded_double_quote_is_escaped(self):
        out = invoices_to_csv([_invoice(customer='Say "hi"')])
        rows = list(csv.reader(io.StringIO(out)))
        assert len(rows[1]) == 5
        assert rows[1][1] == 'Say "hi"'


class TestAmountFormatting:
    @pytest.mark.parametrize(
        ("amount", "expected"),
        [
            (1250.5, "1250.50"),
            (980, "980.00"),
            (20, "20.00"),
            (Decimal("1250.5"), "1250.50"),
        ],
    )
    def test_two_decimals(self, amount, expected):
        out = invoices_to_csv([_invoice(amount=amount)])
        assert _field(out, 3) == expected

    @pytest.mark.parametrize(
        ("amount", "expected"),
        [
            (1250.567, "1250.57"),
            (2.675, "2.68"),
            (Decimal("0.005"), "0.01"),
        ],
    )
    def test_rounds_half_up(self, amount, expected):
        out = invoices_to_csv([_invoice(amount=amount)])
        assert _field(out, 3) == expected


class TestDateFormatting:
    def test_zero_padded_iso_date(self):
        out = invoices_to_csv([_invoice(date=date(2026, 3, 1))])
        assert _field(out, 2) == "2026-03-01"

    def test_datetime_emits_calendar_date_only(self):
        out = invoices_to_csv([_invoice(date=datetime(2026, 3, 1, 13, 5))])
        assert _field(out, 2) == "2026-03-01"


class TestPackageExports:
    def test_root_import_and_all(self):
        assert testbed_utils.invoices_to_csv is invoicecsv.invoices_to_csv
        assert "invoices_to_csv" in testbed_utils.__all__


def public_functions():
    return [
        obj
        for name, obj in vars(invoicecsv).items()
        if not name.startswith("_")
        and inspect.isfunction(obj)
        and obj.__module__ == invoicecsv.__name__
    ]


class TestDocstringExamples:
    def test_every_public_function_is_covered(self):
        assert {f.__name__ for f in public_functions()} == {"invoices_to_csv"}

    def test_every_public_function_has_a_runnable_example(self):
        found = {
            test.name.rsplit(".", 1)[-1]: test
            for test in doctest.DocTestFinder().find(invoicecsv)
        }
        for func in public_functions():
            test = found.get(func.__name__)
            assert test is not None, f"{func.__name__} has no docstring"
            assert test.examples, f"{func.__name__} docstring has no >>> example"

    def test_doctests_pass(self):
        results = doctest.testmod(invoicecsv)
        assert results.attempted > 0
        assert results.failed == 0

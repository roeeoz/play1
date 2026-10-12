import doctest
import inspect
from decimal import Decimal
from types import SimpleNamespace

import testbed_utils
from testbed_utils import invoices
from testbed_utils.invoices import invoice_net_amount


def _line(amount: str) -> SimpleNamespace:
    return SimpleNamespace(amount=Decimal(amount))


class TestInvoiceNetAmount:
    def test_no_lines(self):
        assert invoice_net_amount([]) == Decimal(0)

    def test_one_line(self):
        assert invoice_net_amount([_line("42.50")]) == Decimal("42.50")

    def test_several_lines(self):
        lines = [_line("10.00"), _line("20.00"), _line("5.75")]
        assert invoice_net_amount(lines) == Decimal("35.75")


class TestPackageExports:
    def test_root_import_and_all(self):
        from testbed_utils import invoice_net_amount as root_fn

        assert root_fn is invoice_net_amount
        assert "invoice_net_amount" in testbed_utils.__all__


def public_functions():
    return [
        obj
        for name, obj in vars(invoices).items()
        if not name.startswith("_")
        and inspect.isfunction(obj)
        and obj.__module__ == invoices.__name__
    ]


class TestDocstringExamples:
    def test_every_public_function_has_a_runnable_example(self):
        found = {
            test.name.rsplit(".", 1)[-1]: test
            for test in doctest.DocTestFinder().find(invoices)
        }
        for func in public_functions():
            test = found.get(func.__name__)
            assert test is not None, f"{func.__name__} has no docstring"
            assert test.examples, f"{func.__name__} docstring has no >>> example"

    def test_doctests_pass(self):
        results = doctest.testmod(invoices)
        assert results.attempted > 0
        assert results.failed == 0

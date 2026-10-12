from decimal import Decimal
from types import SimpleNamespace

import testbed_utils
from testbed_utils.invoiceutils import invoice_tax_total


class TestInvoiceTaxTotal:
    def test_no_lines(self):
        assert invoice_tax_total([]) == Decimal("0")

    def test_one_line(self):
        lines = [SimpleNamespace(tax=Decimal("10.50"))]
        assert invoice_tax_total(lines) == Decimal("10.50")

    def test_several_lines(self):
        lines = [
            SimpleNamespace(tax=Decimal("10.00")),
            SimpleNamespace(tax=Decimal("5.25")),
            SimpleNamespace(tax=Decimal("3.75")),
        ]
        assert invoice_tax_total(lines) == Decimal("19.00")


class TestPackageExports:
    def test_root_import_and_all(self):
        from testbed_utils import invoice_tax_total as root_fn

        assert root_fn is invoice_tax_total
        assert "invoice_tax_total" in testbed_utils.__all__

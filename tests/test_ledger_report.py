import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from ledger import RATES, CategoryTotal, LedgerError, MonthlyReport, Transaction, monthly_report, parse_csv

SAMPLE = Path(__file__).parent / "fixtures" / "ledger" / "sample.csv"
D = Decimal


@pytest.fixture(scope="module")
def sample():
    return parse_csv(SAMPLE)


def tx(amount, currency="ILS", category="misc", day=1, tx_id=None):
    return Transaction(
        id=tx_id or f"{category}-{amount}-{day}",
        date=datetime.date(2026, 3, day),
        amount=D(amount),
        currency=currency,
        category=category,
        memo="",
    )


class TestMarchInIls:
    def test_figures(self, sample):
        report = monthly_report(sample, "2026-03")
        assert isinstance(report, MonthlyReport)
        assert report.month == "2026-03"
        assert report.base == "ILS"
        assert report.count == 7
        assert report.income == D("12925.00")
        assert report.expense == D("-3025.50")
        assert report.net == D("9899.50")

    def test_categories_ordered_by_absolute_total(self, sample):
        report = monthly_report(sample, "2026-03")
        assert report.categories == [
            CategoryTotal("salary", D("12000.00"), 1),
            CategoryTotal("rent", D("-1500.00"), 1),
            CategoryTotal("freelance", D("925.00"), 1),
            CategoryTotal("groceries", D("-760.50"), 2),
            CategoryTotal("software", D("-444.00"), 1),
            CategoryTotal("travel", D("-321.00"), 1),
        ]


class TestBaseCurrency:
    def test_usd(self, sample):
        report = monthly_report(sample, "2026-03", base="USD")
        assert report.base == "USD"
        totals = {c.name: c.total for c in report.categories}
        assert totals["salary"] == D("3243.24")
        assert totals["freelance"] == D("250.00")
        assert report.income == D("3493.24")
        assert report.expense == D("-817.70")
        assert report.net == D("2675.54")

    def test_rates_constant(self):
        assert RATES == {"ILS": D("1"), "USD": D("3.70"), "EUR": D("4.00")}

    def test_custom_rates(self):
        rates = {"ILS": D(1), "USD": D(2), "EUR": D(4)}
        report = monthly_report([tx("10", "USD")], "2026-03", rates=rates)
        assert report.income == D("20.00")


class TestRounding:
    def test_single_half_even(self):
        report = monthly_report([tx("0.05")], "2026-03", base="EUR")
        assert report.income == D("0.01")

    def test_rounded_once_after_summing(self):
        txs = [tx("0.05", day=d) for d in (1, 2, 3)]
        report = monthly_report(txs, "2026-03", base="EUR")
        assert report.income == D("0.04")
        assert report.categories[0].total == D("0.04")

    def test_two_places_always(self):
        report = monthly_report([tx("5", category="a"), tx("-2", category="b")], "2026-03")
        assert str(report.income) == "5.00"
        assert str(report.expense) == "-2.00"
        assert str(report.net) == "3.00"
        assert [str(c.total) for c in report.categories] == ["5.00", "-2.00"]


class TestTopAndOrdering:
    def test_top_two(self, sample):
        report = monthly_report(sample, "2026-03", top=2)
        assert [c.name for c in report.categories] == ["salary", "rent"]
        assert report.count == 7
        assert report.income == D("12925.00")
        assert report.expense == D("-3025.50")
        assert report.net == D("9899.50")

    def test_top_larger_than_categories_keeps_all(self, sample):
        assert len(monthly_report(sample, "2026-03", top=50).categories) == 6

    def test_top_none_keeps_all(self, sample):
        assert len(monthly_report(sample, "2026-03", top=None).categories) == 6

    def test_ties_by_name(self):
        txs = [tx("-10", category="zeta"), tx("10", category="alpha"), tx("-10", category="mid")]
        report = monthly_report(txs, "2026-03")
        assert [c.name for c in report.categories] == ["alpha", "mid", "zeta"]


class TestMonthSelection:
    def test_empty_month(self, sample):
        report = monthly_report(sample, "2026-05")
        assert report.count == 0
        assert report.income == D("0.00")
        assert report.expense == D("0.00")
        assert report.net == D("0.00")
        assert report.categories == []
        assert report.to_dict() == {
            "month": "2026-05",
            "base": "ILS",
            "count": 0,
            "income": "0.00",
            "expense": "0.00",
            "net": "0.00",
            "categories": [],
        }

    def test_february_only(self, sample):
        report = monthly_report(sample, "2026-02")
        assert report.categories == [CategoryTotal("groceries", D("-99.99"), 1)]

    def test_to_dict_amounts_are_strings(self, sample):
        data = monthly_report(sample, "2026-03", base="USD", top=1).to_dict()
        assert data["categories"] == [{"name": "salary", "total": "3243.24", "count": 1}]
        assert data["income"] == "3493.24"


class TestArgumentErrors:
    @pytest.mark.parametrize("month", ["2026-3", "2026-13", "2026-00", "March 2026", "202603", ""])
    def test_bad_month(self, sample, month):
        with pytest.raises(ValueError):
            monthly_report(sample, month)

    def test_unknown_base(self, sample):
        with pytest.raises(ValueError):
            monthly_report(sample, "2026-03", base="GBP")

    @pytest.mark.parametrize("top", [0, -1])
    def test_top_below_one(self, sample, top):
        with pytest.raises(ValueError):
            monthly_report(sample, "2026-03", top=top)

    def test_caller_errors_are_not_ledger_errors(self, sample):
        with pytest.raises(ValueError) as info:
            monthly_report(sample, "2026-13")
        assert not isinstance(info.value, LedgerError)

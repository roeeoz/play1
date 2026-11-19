import dataclasses
import datetime
import decimal
import pathlib
from decimal import Decimal

import pytest

from ledger import (
    RATES,
    CategoryTotal,
    LedgerError,
    MonthlyReport,
    Transaction,
    monthly_report,
    parse_csv,
)

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "ledger"


@pytest.fixture(scope="module")
def sample():
    return parse_csv(FIXTURES / "sample.csv")


_ids = iter(range(10**6))


def tx(amount, currency="ILS", category="misc", date="2026-03-15"):
    return Transaction(
        id=f"x{next(_ids)}",
        date=datetime.date.fromisoformat(date),
        amount=Decimal(amount),
        currency=currency,
        category=category,
        memo="",
    )


def cats(report):
    return [(c.name, str(c.total), c.count) for c in report.categories]


def test_rates_constant():
    assert RATES == {"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}


class TestSampleMarch:
    def test_ils_report(self, sample):
        r = monthly_report(sample, "2026-03")
        assert isinstance(r, MonthlyReport)
        assert (r.month, r.base, r.count) == ("2026-03", "ILS", 7)
        assert r.income == Decimal("12925.00")
        assert r.expense == Decimal("-3025.50")
        assert r.net == Decimal("9899.50")
        assert list(r.categories) == [
            CategoryTotal("salary", Decimal("12000.00"), 1),
            CategoryTotal("rent", Decimal("-1500.00"), 1),
            CategoryTotal("freelance", Decimal("925.00"), 1),
            CategoryTotal("groceries", Decimal("-760.50"), 2),
            CategoryTotal("software", Decimal("-444.00"), 1),
            CategoryTotal("travel", Decimal("-321.00"), 1),
        ]

    def test_usd_report(self, sample):
        r = monthly_report(sample, "2026-03", base="USD")
        assert r.base == "USD"
        totals = {c.name: str(c.total) for c in r.categories}
        assert totals["salary"] == "3243.24"
        assert totals["freelance"] == "250.00"
        assert (str(r.income), str(r.expense), str(r.net)) == ("3493.24", "-817.70", "2675.54")

    def test_top_n(self, sample):
        r = monthly_report(sample, "2026-03", top=2)
        assert [c.name for c in r.categories] == ["salary", "rent"]
        assert (r.count, str(r.income), str(r.expense), str(r.net)) == (
            7, "12925.00", "-3025.50", "9899.50")
        assert len(monthly_report(sample, "2026-03", top=100).categories) == 6
        assert len(monthly_report(sample, "2026-03", top=None).categories) == 6

    def test_february_only(self, sample):
        r = monthly_report(sample, "2026-02")
        assert cats(r) == [("groceries", "-99.99", 1)]
        assert r.count == 1

    def test_empty_month(self, sample):
        r = monthly_report(sample, "2026-05")
        assert r.count == 0
        assert r.income == r.expense == r.net == Decimal("0.00")
        assert str(r.net) == "0.00"
        assert len(r.categories) == 0
        assert r.to_dict() == {"month": "2026-05", "base": "ILS", "count": 0, "income": "0.00",
                               "expense": "0.00", "net": "0.00", "categories": []}

    def test_to_dict_non_empty(self, sample):
        d = monthly_report(sample, "2026-03", base="USD", top=1).to_dict()
        assert list(d) == ["month", "base", "count", "income", "expense", "net", "categories"]
        assert d == {"month": "2026-03", "base": "USD", "count": 7, "income": "3493.24",
                     "expense": "-817.70", "net": "2675.54",
                     "categories": [{"name": "salary", "total": "3243.24", "count": 1}]}

    def test_report_is_immutable(self, sample):
        r = monthly_report(sample, "2026-03")
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.net = Decimal("0")
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.categories[0].total = Decimal("0")


class TestRounding:
    def test_round_once_half_even(self):
        assert str(monthly_report([tx("0.05")], "2026-03", base="EUR").income) == "0.01"
        three = [tx("0.05"), tx("0.05"), tx("0.05")]
        assert str(monthly_report(three, "2026-03", base="EUR").income) == "0.04"

    def test_figures_rounded_independently(self):
        r = monthly_report([tx("0.05", category="a"), tx("0.05", category="b"),
                            tx("0.05", category="c")], "2026-03", base="EUR")
        assert str(r.income) == "0.04"
        assert sum(c.total for c in r.categories) == Decimal("0.03")

    def test_global_context_does_not_matter(self):
        with decimal.localcontext() as ctx:
            ctx.prec = 3
            ctx.rounding = decimal.ROUND_UP
            r = monthly_report([tx("12000.00", "USD"), tx("0.05")], "2026-03", base="EUR")
        assert str(r.income) == "11100.01"

    def test_two_places_always(self):
        r = monthly_report([tx("5"), tx("-2")], "2026-03")
        assert (str(r.income), str(r.expense), str(r.net)) == ("5.00", "-2.00", "3.00")

    def test_no_negative_zero(self):
        r = monthly_report([tx("-0.01")], "2026-03", base="EUR")
        assert str(r.expense) == "0.00"
        assert str(r.net) == "0.00"
        assert str(r.categories[0].total) == "0.00"


class TestOrdering:
    def test_ties_by_name(self):
        r = monthly_report([tx("-10", category="zeta"), tx("10", category="alpha"),
                            tx("-10", category="beta")], "2026-03")
        assert [c.name for c in r.categories] == ["alpha", "beta", "zeta"]

    def test_custom_rates(self):
        rates = {"ILS": Decimal(1), "USD": Decimal(2), "EUR": Decimal(4)}
        r = monthly_report([tx("10", "USD")], "2026-03", rates=rates)
        assert str(r.income) == "20.00"


class TestArgumentErrors:
    @pytest.mark.parametrize("month", ["2026-3", "2026-13", "2026-00", "March 2026", "202603", "",
                                       None, "2026-03 "])
    def test_bad_month(self, sample, month):
        with pytest.raises(ValueError) as info:
            monthly_report(sample, month)
        assert not isinstance(info.value, LedgerError)

    def test_bad_base(self, sample):
        with pytest.raises(ValueError):
            monthly_report(sample, "2026-03", base="GBP")

    @pytest.mark.parametrize("top", [0, -1, True, "2", 1.5])
    def test_bad_top(self, sample, top):
        with pytest.raises(ValueError):
            monthly_report(sample, "2026-03", top=top)

    def test_currency_missing_from_rates(self):
        with pytest.raises(ValueError):
            monthly_report([tx("10", "USD")], "2026-03", rates={"ILS": Decimal(1)})

    @pytest.mark.parametrize("rate", [Decimal(0), Decimal(-1)])
    def test_non_positive_rate(self, rate):
        with pytest.raises(ValueError):
            monthly_report([tx("10", "USD")], "2026-03",
                           rates={"ILS": Decimal(1), "USD": rate})
        with pytest.raises(ValueError):
            monthly_report([tx("10")], "2026-03", base="USD",
                           rates={"ILS": Decimal(1), "USD": rate})

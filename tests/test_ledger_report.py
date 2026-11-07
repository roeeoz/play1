import datetime
import decimal
from decimal import Decimal
from pathlib import Path

import pytest

from ledger import (
    RATES,
    CategoryTotal,
    LedgerError,
    Transaction,
    monthly_report,
    parse_csv,
)

SAMPLE = Path(__file__).parent / "fixtures" / "ledger" / "sample.csv"


@pytest.fixture(scope="module")
def sample():
    return parse_csv(SAMPLE)


def tx(amount, currency="ILS", category="c", id=None, date="2026-03-15"):
    tx.n = getattr(tx, "n", 0) + 1
    return Transaction(id or f"x{tx.n}", datetime.date.fromisoformat(date),
                       Decimal(amount), currency, category, "")


def cats(report):
    return [(c.name, str(c.total), c.count) for c in report.categories]


def test_rates_constant():
    assert RATES == {"ILS": Decimal("1"), "USD": Decimal("3.70"),
                     "EUR": Decimal("4.00")}


def test_march_in_ils(sample):
    r = monthly_report(sample, "2026-03")
    assert (r.month, r.base, r.count) == ("2026-03", "ILS", 7)
    assert r.income == Decimal("12925.00")
    assert r.expense == Decimal("-3025.50")
    assert r.net == Decimal("9899.50")
    assert r.categories == [
        CategoryTotal("salary", Decimal("12000.00"), 1),
        CategoryTotal("rent", Decimal("-1500.00"), 1),
        CategoryTotal("freelance", Decimal("925.00"), 1),
        CategoryTotal("groceries", Decimal("-760.50"), 2),
        CategoryTotal("software", Decimal("-444.00"), 1),
        CategoryTotal("travel", Decimal("-321.00"), 1),
    ]


def test_march_in_usd(sample):
    r = monthly_report(sample, "2026-03", base="USD")
    assert r.base == "USD"
    totals = {c.name: str(c.total) for c in r.categories}
    assert totals["salary"] == "3243.24"
    assert totals["freelance"] == "250.00"
    assert (str(r.income), str(r.expense), str(r.net)) == (
        "3493.24", "-817.70", "2675.54")


def test_round_once_half_even():
    assert str(monthly_report([tx("0.05")], "2026-03", base="EUR").income) == "0.01"
    three = [tx("0.05") for _ in range(3)]
    assert str(monthly_report(three, "2026-03", base="EUR").income) == "0.04"


def test_figures_rounded_independently():
    # 0.0125 + 0.0125 - 0.0125 in EUR: each figure is its own exact sum.
    r = monthly_report([tx("0.05", category="a"), tx("0.05", category="b"),
                        tx("-0.05", category="c")], "2026-03", base="EUR")
    assert (str(r.income), str(r.expense), str(r.net)) == ("0.02", "-0.01", "0.01")
    assert cats(r) == [("a", "0.01", 1), ("b", "0.01", 1), ("c", "-0.01", 1)]


def test_two_places_always():
    r = monthly_report([tx("5"), tx("-2")], "2026-03")
    assert (str(r.income), str(r.expense), str(r.net)) == ("5.00", "-2.00", "3.00")


def test_top_n(sample):
    r = monthly_report(sample, "2026-03", top=2)
    assert [c.name for c in r.categories] == ["salary", "rent"]
    assert (r.count, str(r.income), str(r.expense), str(r.net)) == (
        7, "12925.00", "-3025.50", "9899.50")
    assert len(monthly_report(sample, "2026-03", top=99).categories) == 6
    assert len(monthly_report(sample, "2026-03", top=None).categories) == 6


def test_ties_by_name():
    r = monthly_report([tx("10", category="zeta"), tx("-10", category="alpha"),
                        tx("10", category="mid")], "2026-03")
    assert [c.name for c in r.categories] == ["alpha", "mid", "zeta"]


def test_empty_month(sample):
    r = monthly_report(sample, "2026-05")
    assert r.count == 0
    assert r.income == r.expense == r.net == Decimal("0.00")
    assert str(r.net) == "0.00"
    assert r.categories == []
    d = r.to_dict()
    assert d == {"month": "2026-05", "base": "ILS", "count": 0, "income": "0.00",
                 "expense": "0.00", "net": "0.00", "categories": []}
    assert list(d) == ["month", "base", "count", "income", "expense", "net",
                       "categories"]


def test_to_dict_categories(sample):
    d = monthly_report(sample, "2026-03", top=1).to_dict()
    assert d["categories"] == [{"name": "salary", "total": "12000.00", "count": 1}]


def test_month_filter(sample):
    assert cats(monthly_report(sample, "2026-02")) == [("groceries", "-99.99", 1)]


def test_rates_parameter():
    rates = {"ILS": Decimal(1), "USD": Decimal(2), "EUR": Decimal(4)}
    r = monthly_report([tx("10", currency="USD")], "2026-03", rates=rates)
    assert str(r.income) == "20.00"


@pytest.mark.parametrize("month", ["2026-3", "2026-13", "2026-00", "March 2026",
                                   "202603", "", "２０２６-03"])
def test_bad_month(sample, month):
    with pytest.raises(ValueError) as info:
        monthly_report(sample, month)
    assert not isinstance(info.value, LedgerError)


def test_bad_base_and_top(sample):
    with pytest.raises(ValueError):
        monthly_report(sample, "2026-03", base="GBP")
    with pytest.raises(ValueError):
        monthly_report(sample, "2026-03", top=0)
    with pytest.raises(ValueError):
        monthly_report(sample, "2026-03", top=-1)


def test_global_context_untouched(sample):
    ctx = decimal.getcontext()
    before = (ctx.prec, ctx.rounding)
    monthly_report(sample, "2026-03", base="USD")
    assert (decimal.getcontext().prec, decimal.getcontext().rounding) == before


def test_low_global_precision_does_not_leak(sample):
    with decimal.localcontext() as ctx:
        ctx.prec = 3
        r = monthly_report(sample, "2026-03", base="USD")
        assert ctx.prec == 3
    assert str(r.income) == "3493.24"

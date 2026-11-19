"""Tests for the ledger monthly report (SCRUM-34 t2)."""

import dataclasses
from datetime import date
from decimal import ROUND_DOWN, Decimal, localcontext
from pathlib import Path

import pytest

from ledger import RATES, CategoryTotal, LedgerError, Report, Transaction, monthly_report, parse_csv

SAMPLE = Path(__file__).parent / "fixtures" / "ledger" / "sample.csv"
D = Decimal


@pytest.fixture(scope="module")
def sample():
    return parse_csv(SAMPLE)


def tx(n, amount, currency="ILS", category="c", day=date(2026, 3, 1)):
    return Transaction(f"x{n}", day, D(amount), currency, category, "")


def cats(report):
    return [(c.name, str(c.total), c.count) for c in report.categories]


def test_rates_constant():
    assert RATES == {"ILS": D("1"), "USD": D("3.70"), "EUR": D("4.00")}


def test_march_in_ils(sample):
    report = monthly_report(sample, "2026-03")
    assert isinstance(report, Report)
    assert (report.month, report.base, report.count) == ("2026-03", "ILS", 7)
    assert report.income == D("12925.00")
    assert report.expense == D("-3025.50")
    assert report.net == D("9899.50")
    assert report.categories == [
        CategoryTotal("salary", D("12000.00"), 1),
        CategoryTotal("rent", D("-1500.00"), 1),
        CategoryTotal("freelance", D("925.00"), 1),
        CategoryTotal("groceries", D("-760.50"), 2),
        CategoryTotal("software", D("-444.00"), 1),
        CategoryTotal("travel", D("-321.00"), 1),
    ]
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.count = 0  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.categories[0].total = D("0")  # type: ignore[misc]


def test_march_in_usd(sample):
    report = monthly_report(sample, "2026-03", base="USD")
    assert report.base == "USD"
    assert (str(report.income), str(report.expense), str(report.net)) == (
        "3493.24",
        "-817.70",
        "2675.54",
    )
    totals = {c.name: str(c.total) for c in report.categories}
    assert totals["salary"] == "3243.24"
    assert totals["freelance"] == "250.00"


def test_rounding_once_after_summing_half_even():
    assert str(monthly_report([tx(1, "0.05")], "2026-03", base="EUR").income) == "0.01"
    three = [tx(i, "0.05") for i in range(3)]
    report = monthly_report(three, "2026-03", base="EUR")
    assert str(report.income) == "0.04"
    assert cats(report) == [("c", "0.04", 3)]


def test_figures_rounded_independently():
    # income 0.0125 -> 0.01, expense -0.0125 -> -0.01, net 0 -> 0.00; categories likewise
    report = monthly_report(
        [tx(1, "0.05", category="a"), tx(2, "-0.05", category="b")], "2026-03", base="EUR"
    )
    assert (str(report.income), str(report.expense), str(report.net)) == ("0.01", "-0.01", "0.00")


def test_two_places_always():
    report = monthly_report([tx(1, "5"), tx(2, "-2")], "2026-03")
    assert (str(report.income), str(report.expense), str(report.net)) == ("5.00", "-2.00", "3.00")


def test_no_negative_zero():
    # net -0.0025 rounds to zero and must print 0.00, never -0.00
    report = monthly_report(
        [tx(1, "0.01", category="a"), tx(2, "-0.02", category="a")], "2026-03", base="EUR"
    )
    assert str(report.net) == "0.00"
    assert cats(report) == [("a", "0.00", 2)]


def test_independent_of_caller_decimal_context(sample):
    expected = monthly_report(sample, "2026-03", base="USD")
    with localcontext() as ctx:
        ctx.prec = 3
        ctx.rounding = ROUND_DOWN
        assert monthly_report(sample, "2026-03", base="USD") == expected


def test_top_n(sample):
    report = monthly_report(sample, "2026-03", top=2)
    assert cats(report) == [("salary", "12000.00", 1), ("rent", "-1500.00", 1)]
    assert (report.count, str(report.income), str(report.expense), str(report.net)) == (
        7,
        "12925.00",
        "-3025.50",
        "9899.50",
    )
    assert len(monthly_report(sample, "2026-03", top=100).categories) == 6
    assert len(monthly_report(sample, "2026-03", top=None).categories) == 6


def test_ties_ordered_by_name():
    report = monthly_report(
        [tx(1, "-10", category="zeta"), tx(2, "10", category="alpha"), tx(3, "-10", category="mid")],
        "2026-03",
    )
    assert [c.name for c in report.categories] == ["alpha", "mid", "zeta"]


def test_empty_month_is_zero_report(sample):
    report = monthly_report(sample, "2026-05")
    assert report.count == 0
    assert report.income == report.expense == report.net == D("0.00")
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
    assert list(report.to_dict()) == ["month", "base", "count", "income", "expense", "net", "categories"]


def test_to_dict_categories(sample):
    data = monthly_report(sample, "2026-03", base="USD", top=1).to_dict()
    assert data["categories"] == [{"name": "salary", "total": "3243.24", "count": 1}]
    assert list(data["categories"][0]) == ["name", "total", "count"]


def test_only_the_month_counts(sample):
    assert cats(monthly_report(sample, "2026-02")) == [("groceries", "-99.99", 1)]


def test_rates_are_a_parameter():
    rates = {"ILS": D(1), "USD": D(2), "EUR": D(4)}
    assert str(monthly_report([tx(1, "10", "USD")], "2026-03", rates=rates).income) == "20.00"


@pytest.mark.parametrize("month", ["2026-3", "2026-13", "2026-00", "March 2026", "202603", "", "2026-03\n"])
def test_bad_month_is_value_error(sample, month):
    with pytest.raises(ValueError):
        monthly_report(sample, month)


@pytest.mark.parametrize(
    "kwargs",
    [{"base": "GBP"}, {"base": "usd"}, {"top": 0}, {"top": -1}, {"top": True}],
)
def test_bad_arguments_are_value_error(sample, kwargs):
    with pytest.raises(ValueError) as info:
        monthly_report(sample, "2026-03", **kwargs)
    assert not isinstance(info.value, LedgerError)


def test_missing_rate_for_a_month_transaction_is_value_error():
    with pytest.raises(ValueError, match="EUR"):
        monthly_report([tx(1, "5", "EUR")], "2026-03", rates={"ILS": D(1)})
    # a transaction outside the month does not need a rate
    other = tx(2, "5", "EUR", day=date(2026, 4, 1))
    assert monthly_report([other], "2026-03", rates={"ILS": D(1)}).count == 0

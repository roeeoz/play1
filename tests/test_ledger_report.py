import datetime
import pathlib
from decimal import Decimal

import pytest

from ledger import RATES, CategoryTotal, LedgerError, Transaction, monthly_report, parse_csv

SAMPLE = pathlib.Path(__file__).parent / "fixtures" / "ledger" / "sample.csv"


@pytest.fixture(scope="module")
def sample():
    return parse_csv(SAMPLE)


def txn(amount, currency="ILS", category="misc", id_="x", day=1):
    return Transaction(id_, datetime.date(2026, 3, day), Decimal(amount), currency, category, "")


def test_rates_constant():
    assert RATES == {"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}


def test_march_in_ils(sample):
    report = monthly_report(sample, "2026-03")

    assert (report.month, report.base, report.count) == ("2026-03", "ILS", 7)
    assert report.income == Decimal("12925.00")
    assert report.expense == Decimal("-3025.50")
    assert report.net == Decimal("9899.50")
    assert report.categories == [
        CategoryTotal("salary", Decimal("12000.00"), 1),
        CategoryTotal("rent", Decimal("-1500.00"), 1),
        CategoryTotal("freelance", Decimal("925.00"), 1),
        CategoryTotal("groceries", Decimal("-760.50"), 2),
        CategoryTotal("software", Decimal("-444.00"), 1),
        CategoryTotal("travel", Decimal("-321.00"), 1),
    ]


def test_march_in_usd(sample):
    report = monthly_report(sample, "2026-03", base="USD")

    totals = {c.name: str(c.total) for c in report.categories}
    assert report.base == "USD"
    assert totals["salary"] == "3243.24"
    assert totals["freelance"] == "250.00"
    assert (str(report.income), str(report.expense), str(report.net)) == (
        "3493.24",
        "-817.70",
        "2675.54",
    )


def test_half_even_single_rounding():
    one = monthly_report([txn("0.05")], "2026-03", base="EUR")
    three = monthly_report(
        [txn("0.05", id_=f"x{i}") for i in range(3)], "2026-03", base="EUR"
    )

    assert one.income == Decimal("0.01")
    assert three.income == Decimal("0.04")
    assert three.categories[0].total == Decimal("0.04")


def test_two_places_always():
    report = monthly_report([txn("5", id_="a"), txn("-2", id_="b")], "2026-03")

    assert (str(report.income), str(report.expense), str(report.net)) == ("5.00", "-2.00", "3.00")


def test_top_n_limits_categories_only(sample):
    report = monthly_report(sample, "2026-03", top=2)

    assert [c.name for c in report.categories] == ["salary", "rent"]
    assert report.count == 7
    assert report.income == Decimal("12925.00")
    assert report.expense == Decimal("-3025.50")
    assert report.net == Decimal("9899.50")
    assert len(monthly_report(sample, "2026-03", top=50).categories) == 6
    assert len(monthly_report(sample, "2026-03", top=None).categories) == 6


def test_ties_ordered_by_name():
    report = monthly_report(
        [txn("10", category="zeta", id_="a"), txn("-10", category="alpha", id_="b")], "2026-03"
    )

    assert [c.name for c in report.categories] == ["alpha", "zeta"]


def test_empty_month_is_zero_report(sample):
    report = monthly_report(sample, "2026-05")

    assert report.count == 0
    assert report.income == report.expense == report.net == Decimal("0.00")
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


def test_to_dict_amounts_are_strings(sample):
    data = monthly_report(sample, "2026-03", top=1).to_dict()

    assert data["income"] == "12925.00"
    assert data["categories"] == [{"name": "salary", "total": "12000.00", "count": 1}]


def test_only_the_months_transactions_count(sample):
    report = monthly_report(sample, "2026-02")

    assert report.categories == [CategoryTotal("groceries", Decimal("-99.99"), 1)]


def test_custom_rates():
    rates = {"ILS": Decimal(1), "USD": Decimal(2), "EUR": Decimal(4)}
    report = monthly_report([txn("10", currency="USD")], "2026-03", rates=rates)

    assert report.income == Decimal("20.00")


@pytest.mark.parametrize("month", ["2026-3", "2026-13", "2026-00", "March 2026", "202603", ""])
def test_bad_month_is_value_error(sample, month):
    with pytest.raises(ValueError):
        monthly_report(sample, month)


def test_unknown_base_is_value_error(sample):
    with pytest.raises(ValueError) as caught:
        monthly_report(sample, "2026-03", base="GBP")
    assert not isinstance(caught.value, LedgerError)


@pytest.mark.parametrize("top", [0, -1])
def test_top_below_one_is_value_error(sample, top):
    with pytest.raises(ValueError):
        monthly_report(sample, "2026-03", top=top)

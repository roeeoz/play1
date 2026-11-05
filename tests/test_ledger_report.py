import datetime
import pathlib
from decimal import Decimal

import pytest

from ledger import RATES, CategoryTotal, LedgerError, Transaction, monthly_report, parse_csv

SAMPLE = pathlib.Path(__file__).parent / "fixtures" / "ledger" / "sample.csv"
D = Decimal


@pytest.fixture(scope="module")
def sample():
    return parse_csv(SAMPLE)


def tx(amount, currency="ILS", category="c", day=1, tid=None):
    return Transaction(
        tid or f"{category}{amount}{day}", datetime.date(2026, 3, day), D(amount),
        currency, category, "",
    )


def test_rates_constant():
    assert RATES == {"ILS": D("1"), "USD": D("3.70"), "EUR": D("4.00")}


def test_march_in_ils(sample):
    report = monthly_report(sample, "2026-03")
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


def test_base_usd(sample):
    report = monthly_report(sample, "2026-03", base="USD")
    assert report.base == "USD"
    totals = {c.name: c.total for c in report.categories}
    assert str(totals["salary"]) == "3243.24"
    assert str(totals["freelance"]) == "250.00"
    assert str(report.income) == "3493.24"
    assert str(report.expense) == "-817.70"
    assert str(report.net) == "2675.54"


def test_round_once_half_even():
    assert monthly_report([tx("0.05")], "2026-03", base="EUR").income == D("0.01")
    three = [tx("0.05", day=d) for d in (1, 2, 3)]
    report = monthly_report(three, "2026-03", base="EUR")
    assert report.income == D("0.04")
    assert report.categories[0].total == D("0.04")


def test_figures_rounded_independently():
    # 0.05 ILS and -0.03 ILS in EUR: income 0.0125 -> 0.01, expense -0.0075 -> -0.01,
    # net 0.005 -> 0.00, so income + expense != net by design.
    report = monthly_report([tx("0.05", category="a"), tx("-0.03", category="b")],
                            "2026-03", base="EUR")
    assert (report.income, report.expense, report.net) == (D("0.01"), D("-0.01"), D("0.00"))


def test_two_places_always():
    report = monthly_report([tx("5"), tx("-2", day=2)], "2026-03")
    assert (str(report.income), str(report.expense), str(report.net)) == ("5.00", "-2.00", "3.00")
    assert str(report.categories[0].total) == "3.00"


def test_top_n(sample):
    report = monthly_report(sample, "2026-03", top=2)
    assert [c.name for c in report.categories] == ["salary", "rent"]
    assert report.count == 7
    assert (report.income, report.expense, report.net) == (D("12925.00"), D("-3025.50"), D("9899.50"))
    assert len(monthly_report(sample, "2026-03", top=50).categories) == 6
    assert len(monthly_report(sample, "2026-03", top=None).categories) == 6


def test_ties_by_name():
    report = monthly_report([tx("-10", category="zeta"), tx("10", category="alpha")], "2026-03")
    assert [c.name for c in report.categories] == ["alpha", "zeta"]


def test_empty_month(sample):
    report = monthly_report(sample, "2026-05")
    assert report.count == 0
    assert report.income == report.expense == report.net == D("0.00")
    assert report.categories == []
    assert report.to_dict() == {
        "month": "2026-05", "base": "ILS", "count": 0, "income": "0.00",
        "expense": "0.00", "net": "0.00", "categories": [],
    }


def test_to_dict_categories(sample):
    data = monthly_report(sample, "2026-03", top=1).to_dict()
    assert data["categories"] == [{"name": "salary", "total": "12000.00", "count": 1}]


def test_only_the_month_counts(sample):
    report = monthly_report(sample, "2026-02")
    assert report.categories == [CategoryTotal("groceries", D("-99.99"), 1)]
    assert report.count == 1


def test_custom_rates():
    rates = {"ILS": D(1), "USD": D(2), "EUR": D(4)}
    assert monthly_report([tx("10", "USD")], "2026-03", rates=rates).income == D("20.00")


@pytest.mark.parametrize("month", ["2026-3", "2026-13", "2026-00", "March 2026", "202603", ""])
def test_bad_month(sample, month):
    with pytest.raises(ValueError):
        monthly_report(sample, month)


def test_bad_base(sample):
    with pytest.raises(ValueError):
        monthly_report(sample, "2026-03", base="GBP")


@pytest.mark.parametrize("top", [0, -1])
def test_bad_top(sample, top):
    with pytest.raises(ValueError) as info:
        monthly_report(sample, "2026-03", top=top)
    assert not isinstance(info.value, LedgerError)

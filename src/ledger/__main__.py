"""Command line: ``python -m ledger report FILE --month YYYY-MM [...]``.

Exit codes: 0 success, 2 usage error (including an unreadable FILE),
3 a bad ledger row.
"""

from __future__ import annotations

import argparse
import json
import sys

from ledger.model import CURRENCIES, LedgerError
from ledger.parse import parse_csv
from ledger.report import MonthlyReport, is_month, monthly_report


def _month(text: str) -> str:
    if not is_month(text):
        raise argparse.ArgumentTypeError(f"{text!r} is not YYYY-MM (month 01-12)")
    return text


def _top(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not an integer") from None
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {value}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ledger", description="Reports from a CSV expense ledger."
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)
    report = commands.add_parser(
        "report", help="total one month by category in a base currency"
    )
    report.add_argument("file", metavar="FILE", help="ledger CSV file")
    report.add_argument(
        "--month", required=True, type=_month, metavar="YYYY-MM", help="month to report"
    )
    report.add_argument(
        "--base", choices=CURRENCIES, default="ILS", help="base currency (default: ILS)"
    )
    report.add_argument(
        "--top", type=_top, default=None, metavar="N", help="keep only the N largest categories"
    )
    report.add_argument("--json", action="store_true", help="print the report as JSON")
    return parser


def render_text(report: MonthlyReport) -> str:
    lines = [
        f"month: {report.month}",
        f"base: {report.base}",
        f"transactions: {report.count}",
        f"income: {report.income}",
        f"expense: {report.expense}",
        f"net: {report.net}",
    ]
    if report.categories:
        lines.append("categories:")
        lines.extend(f"  {c.name}: {c.total} ({c.count})" for c in report.categories)
    else:
        lines.append("categories: none")
    return "".join(line + "\n" for line in lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        transactions = parse_csv(args.file)
    except LedgerError as error:
        sys.stderr.write(f"error: {args.file}:{error.line}: {error.reason}\n")
        return 3
    except OSError as error:
        sys.stderr.write(f"error: cannot read {args.file}: {error.strerror}\n")
        return 2
    report = monthly_report(transactions, args.month, base=args.base, top=args.top)
    if args.json:
        sys.stdout.write(json.dumps(report.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(render_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())

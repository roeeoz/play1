"""Command line: ``python -m ledger report FILE --month YYYY-MM``.

Exit codes: 0 success, 2 usage error (incl. unreadable FILE), 3 data error.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from ledger.parser import LedgerError, parse_csv
from ledger.report import RATES, MonthlyReport, is_month, monthly_report

EXIT_DATA = 3


def _month(text: str) -> str:
    if not is_month(text):
        raise argparse.ArgumentTypeError(f"invalid month {text!r}: expected YYYY-MM")
    return text


def _top(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid top {text!r}: expected an integer") from None
    if value < 1:
        raise argparse.ArgumentTypeError(f"invalid top {text!r}: must be at least 1")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ledger", description="Reports from a CSV ledger."
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")
    commands.required = True
    report = commands.add_parser(
        "report",
        help="total one month by category",
        description="Total one month of a CSV ledger by category in a base currency.",
    )
    report.add_argument("file", metavar="FILE", help="ledger CSV file (UTF-8)")
    report.add_argument(
        "--month", required=True, type=_month, help="month to report, as YYYY-MM"
    )
    report.add_argument(
        "--base",
        choices=tuple(RATES),
        default="ILS",
        help="base currency for all figures (default: ILS)",
    )
    report.add_argument(
        "--top", type=_top, default=None, help="list only the N largest categories (N >= 1)"
    )
    report.add_argument(
        "--json", action="store_true", help="print one JSON object instead of text"
    )
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


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        transactions = parse_csv(args.file)
    except LedgerError as exc:
        sys.stderr.write(f"error: {args.file}:{exc.line}: {exc.reason}\n")
        return EXIT_DATA
    except (OSError, UnicodeDecodeError) as exc:
        parser.error(f"cannot read {args.file}: {exc}")
    report = monthly_report(transactions, args.month, base=args.base, top=args.top)
    if args.json:
        output = json.dumps(report.to_dict()) + "\n"
    else:
        output = render_text(report)
    sys.stdout.write(output)
    return 0

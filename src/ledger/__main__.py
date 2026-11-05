"""Command line: ``python -m ledger report FILE --month YYYY-MM``.

Exit codes: 0 success, 2 usage error (including an unreadable FILE),
3 a data error in the ledger.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence

from ledger.model import CURRENCIES, LedgerError
from ledger.parse import parse_csv
from ledger.report import MonthlyReport, monthly_report

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_DATA = 3

_MONTH_RE = re.compile(r"[0-9]{4}-(0[1-9]|1[0-2])")


def _month(text: str) -> str:
    if not _MONTH_RE.fullmatch(text):
        raise argparse.ArgumentTypeError(f"'{text}' is not YYYY-MM with a month of 01-12")
    return text


def _top(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{text}' is not an integer") from None
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {value}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ledger",
        description="Summarise a CSV ledger.",
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)
    report = commands.add_parser(
        "report",
        help="total one month by category in a base currency",
        description="Total one month of a CSV ledger by category in a base currency.",
    )
    report.add_argument("file", metavar="FILE", help="UTF-8 CSV ledger file")
    report.add_argument("--month", required=True, type=_month, metavar="YYYY-MM",
                        help="the month to report, e.g. 2026-03")
    report.add_argument("--base", choices=CURRENCIES, default="ILS",
                        help="currency to report in (default: ILS)")
    report.add_argument("--top", type=_top, default=None, metavar="N",
                        help="keep only the N largest categories")
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


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        transactions = parse_csv(args.file)
    except LedgerError as exc:
        sys.stderr.write(f"error: {args.file}:{exc.line}: {exc.reason}\n")
        return EXIT_DATA
    except OSError as exc:
        sys.stderr.write(f"error: cannot read {args.file}: {exc.strerror}\n")
        return EXIT_USAGE

    report = monthly_report(transactions, args.month, base=args.base, top=args.top)
    if args.json:
        sys.stdout.write(json.dumps(report.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(render_text(report))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())

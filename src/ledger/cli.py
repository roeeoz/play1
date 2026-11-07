"""Command line: ``python -m ledger report FILE --month YYYY-MM ...``.

Exit codes: 0 on success, 2 on a usage error (including a FILE that cannot be
opened or decoded), 3 on a data error in the ledger. On any error stdout is
left empty.
"""

from __future__ import annotations

import argparse
import json
import sys

from ledger.parser import LedgerError, parse_csv
from ledger.report import RATES, MonthlyReport, _check_month, monthly_report


def _month(text: str) -> str:
    try:
        return _check_month(text)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid month {text!r}: expected YYYY-MM with a month of 01-12"
        ) from None


def _top(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        value = 0
    if value < 1:
        raise argparse.ArgumentTypeError(
            f"invalid top {text!r}: expected an integer of at least 1"
        )
    return value


def _build_parser() -> tuple[argparse.ArgumentParser, argparse.ArgumentParser]:
    parser = argparse.ArgumentParser(
        prog="python -m ledger",
        description="Reports over a CSV ledger.",
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")
    commands.required = True
    report = commands.add_parser(
        "report",
        help="total one month by category in a base currency",
        description="Total one month of a CSV ledger by category in a base currency.",
    )
    report.add_argument("file", metavar="FILE", help="the CSV ledger to read")
    report.add_argument("--month", required=True, type=_month, metavar="YYYY-MM",
                        help="the month to report, e.g. 2026-03")
    report.add_argument("--base", choices=list(RATES), default="ILS",
                        help="currency to report in (default: ILS)")
    report.add_argument("--top", type=_top, default=None, metavar="N",
                        help="show only the N largest categories")
    report.add_argument("--json", action="store_true",
                        help="print the report as a JSON object")
    return parser, report


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
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser, report_parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        transactions = parse_csv(args.file)
    except LedgerError as error:
        sys.stderr.write(f"error: {args.file}:{error.line}: {error.reason}\n")
        return 3
    except UnicodeDecodeError:
        report_parser.error(f"cannot read {args.file}: not valid UTF-8")
    except OSError as error:
        report_parser.error(f"cannot open {args.file}: {error.strerror or error}")
    report = monthly_report(transactions, args.month, base=args.base, top=args.top)
    if args.json:
        output = json.dumps(report.to_dict()) + "\n"
    else:
        output = render_text(report)
    sys.stdout.write(output)
    return 0

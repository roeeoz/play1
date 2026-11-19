"""Command line: ``python -m ledger report FILE --month YYYY-MM ...``."""

from __future__ import annotations

import argparse
import json
import sys

from ledger.parser import CURRENCIES, LedgerError, parse_csv
from ledger.report import MONTH_RE, Report, monthly_report


def _month(text: str) -> str:
    if MONTH_RE.fullmatch(text) is None:
        raise argparse.ArgumentTypeError(f"invalid month {text!r}: expected YYYY-MM with month 01-12")
    return text


def _top(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid top {text!r}: expected an integer") from None
    if value < 1:
        raise argparse.ArgumentTypeError(f"invalid top {text!r}: must be at least 1")
    return value


def build_parser() -> tuple[argparse.ArgumentParser, argparse.ArgumentParser]:
    parser = argparse.ArgumentParser(
        prog="python -m ledger", description="Reports from a CSV ledger."
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)
    report = commands.add_parser(
        "report",
        help="total one month by category",
        description="Total one month of a CSV ledger by category in a base currency.",
    )
    report.add_argument("file", metavar="FILE", help="UTF-8 CSV ledger file")
    report.add_argument(
        "--month", required=True, type=_month, metavar="YYYY-MM", help="month to report, e.g. 2026-03"
    )
    report.add_argument(
        "--base", choices=CURRENCIES, default="ILS", help="base currency (default: ILS)"
    )
    report.add_argument(
        "--top", type=_top, metavar="N", help="list only the N largest categories (N >= 1)"
    )
    report.add_argument("--json", action="store_true", help="print the report as one JSON object")
    return parser, report


def render_text(report: Report) -> str:
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


def render_json(report: Report) -> str:
    return json.dumps(report.to_dict()) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser, report_parser = build_parser()
    args = parser.parse_args(argv)
    try:
        transactions = parse_csv(args.file)
    except LedgerError as error:
        sys.stderr.write(f"error: {args.file}:{error.line}: {error.reason}\n")
        return 3
    except UnicodeDecodeError as error:
        report_parser.error(f"cannot read {args.file}: not valid UTF-8 ({error.reason})")
    except OSError as error:
        report_parser.error(f"cannot open {args.file}: {error.strerror or error}")
    report = monthly_report(transactions, args.month, base=args.base, top=args.top)
    output = render_json(report) if args.json else render_text(report)
    sys.stdout.write(output)
    return 0

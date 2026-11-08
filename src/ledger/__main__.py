"""Command line: ``python -m ledger report FILE --month YYYY-MM``.

Exit codes: 0 success, 2 usage error (including an unreadable FILE),
3 data error (a bad ledger row).
"""

from __future__ import annotations

import argparse
import json
import re
import sys

from ledger.model import CURRENCIES, LedgerError
from ledger.parse import parse_csv
from ledger.report import MonthlyReport, monthly_report

_MONTH_RE = re.compile(r"\d{4}-(0[1-9]|1[0-2])")


def _month(text: str) -> str:
    if not _MONTH_RE.fullmatch(text):
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
        "report", help="total one month by category",
        description="Total one month of a CSV ledger by category in a base currency.",
    )
    report.add_argument("file", metavar="FILE", help="ledger CSV file")
    report.add_argument("--month", required=True, type=_month, metavar="YYYY-MM",
                        help="month to report, e.g. 2026-03")
    report.add_argument("--base", choices=CURRENCIES, default="ILS",
                        help="base currency (default: ILS)")
    report.add_argument("--top", type=_top, default=None, metavar="N",
                        help="keep only the N largest categories")
    report.add_argument("--json", action="store_true", help="print JSON instead of text")
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
    args = build_parser().parse_args(argv)
    try:
        transactions = parse_csv(args.file)
    except OSError as exc:
        print(f"error: cannot read {args.file}: {exc.strerror}", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print(f"error: cannot read {args.file}: not valid UTF-8 text", file=sys.stderr)
        return 2
    except LedgerError as exc:
        print(f"error: {args.file}:{exc.line}: {exc.reason}", file=sys.stderr)
        return 3
    report = monthly_report(transactions, args.month, base=args.base, top=args.top)
    if args.json:
        sys.stdout.write(json.dumps(report.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(render_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())

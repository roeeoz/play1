import argparse
import os
import sys


def _read_stdin() -> str:
    text = sys.stdin.read()
    if not text.strip():
        print("Error: No input provided.", file=sys.stderr)
        sys.exit(1)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize text from stdin using OpenAI."
    )
    parser.add_argument(
        "--lang",
        default=None,
        help="Output language for the summary (e.g. french, es, Spanish).",
    )
    args = parser.parse_args()

    text = _read_stdin()

    if not os.environ.get("OPENAI_API_KEY"):
        from summarize.mock import mock_summarize

        print(mock_summarize(text))
        sys.exit(0)

    from summarize.openai_summarizer import openai_summarize  # noqa: PLC0415

    try:
        summary = openai_summarize(text, lang=args.lang)
        print(summary)
        sys.exit(0)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

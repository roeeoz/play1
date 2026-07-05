# summarize

A Unix-style CLI tool that reads plain text from stdin, summarizes it via OpenAI, and prints the summary to stdout.

## Usage

```bash
cat report.txt | summarize --lang french
cat report.txt | summarize
echo "Hello world" | summarize
```

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | No* | — | OpenAI API key. If unset, mock mode is activated automatically. |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model to use for summarization. |

*When `OPENAI_API_KEY` is not set, the tool runs in mock mode (see below).

## Options

| Flag | Description |
|---|---|
| `--lang <value>` | Output language (e.g. `french`, `fr`, `Spanish`). If omitted, the summary is in the same language as the input. |

## Mock mode

When `OPENAI_API_KEY` is not set, the tool automatically enters **mock mode**:

- No API call is made.
- The tool outputs `mock summary: <first line of stdin>` to stdout.
- The tool exits with code `0`.

```bash
$ echo "Hello world" | summarize
mock summary: Hello world
```

Mock mode is a first-class feature for use in pipelines and CI environments where no API key is available.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success (including mock mode) |
| non-zero | Failure (empty stdin, API error) |

## Development

```bash
pip install -e '.[dev]'
pytest -v
ruff check .
```

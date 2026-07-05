def mock_summarize(text: str) -> str:
    first_line = text.splitlines()[0] if text.splitlines() else text
    return f"mock summary: {first_line}"

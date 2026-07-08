def greet(name: str) -> str:
    """Return a personalised greeting, or 'Hello, stranger!' for empty input."""
    if not name:
        return "Hello, stranger!"
    return f"Hello, {name}!"

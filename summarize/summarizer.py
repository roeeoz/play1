from typing import Optional, Protocol


class Summarizer(Protocol):
    def summarize(self, text: str, lang: Optional[str] = None) -> str:
        ...

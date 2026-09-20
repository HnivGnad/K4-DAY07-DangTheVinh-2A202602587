import re

from .chunking import RecursiveChunker


class HeadingChunker:
    """Split cleaned Markdown by headings, retaining ancestor headings."""

    def __init__(self, chunk_size: int = 1000) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []

        chunks: list[str] = []
        headings: list[tuple[int, str]] = []
        body: list[str] = []

        def flush() -> None:
            content = "\n".join(body).strip()
            if not content:
                return
            prefix = "\n".join(title for _, title in headings)
            budget = self.chunk_size - len(prefix) - (2 if prefix else 0)
            if budget <= 0:
                raise ValueError("Headings are too long; increase chunk_size")
            for part in RecursiveChunker(chunk_size=budget).chunk(content):
                if part.strip():
                    chunks.append(f"{prefix}\n\n{part}" if prefix else part)

        for line in text.splitlines():
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                flush()
                body = []
                level = len(match.group(1))
                while headings and headings[-1][0] >= level:
                    headings.pop()
                headings.append((level, line.strip()))
            else:
                body.append(line)
        flush()
        return chunks

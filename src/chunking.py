from __future__ import annotations

from email.mime import text
import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

        def chunk(self, text: str) -> list[str]:
            sentences = [
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", text)
                if sentence.strip()
            ]

        size = self.max_sentences_per_chunk
        return [
            " ".join(sentences[i:i + size])
            for i in range(0, len(sentences), size)
        ]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

        def chunk(self, text: str) -> list[str]:
            if self.chunk_size <= 0:
                raise ValueError("chunk_size phải lớn hơn 0")

        return self._split(text, self.separators)

    def _split(
        self,
        current_text: str,
        remaining_separators: list[str],
    ) -> list[str]:
        if not current_text:
            return []

        if len(current_text) <= self.chunk_size:
            return [current_text]

        # Không còn dấu phân cách: cắt theo số ký tự.
        if not remaining_separators or remaining_separators[0] == "":
            return [
                current_text[i:i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # Giữ dấu phân cách ở cuối mỗi phần để không mất nội dung.
        parts = current_text.split(separator)
        pieces = [
            part + separator if i < len(parts) - 1 else part
            for i, part in enumerate(parts)
        ]

        chunks = []
        pending = ""

        for piece in pieces:
            if not piece:
                continue

            if len(piece) > self.chunk_size:
                if pending:
                    chunks.append(pending)
                    pending = ""

                chunks.extend(self._split(piece, next_separators))

            elif len(pending) + len(piece) <= self.chunk_size:
                pending += piece

            else:
                chunks.append(pending)
                pending = piece

        if pending:
            chunks.append(pending)

        return chunks

def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    if len(vec_a) != len(vec_b):
        raise ValueError("Hai vector phải có cùng số chiều")

    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Chạy và so sánh ba chiến lược chia nhỏ."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        if chunk_size <= 0:
            raise ValueError("chunk_size phải lớn hơn 0")

        strategies = {
            "fixed_size": FixedSizeChunker(
                chunk_size=chunk_size,
                overlap=min(50, chunk_size - 1),
            ),
            "by_sentences": SentenceChunker(
                max_sentences_per_chunk=3,
            ),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        results = {}

        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)

            results[name] = {
                "count": count,
                "avg_length": (
                    sum(len(chunk) for chunk in chunks) / count
                    if count else 0.0
                ),
                "chunks": chunks,
            }

        return results
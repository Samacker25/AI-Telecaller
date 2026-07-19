"""Split cleaned document text into overlapping chunks for embedding."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """A contiguous piece of document text ready for embedding."""

    index: int
    text: str


def chunk_text(text: str, *, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """Split text into chunks of roughly ``chunk_size`` characters.

    Paragraphs are kept together when possible; adjacent chunks share
    ``chunk_overlap`` trailing characters of context. Paragraphs longer
    than ``chunk_size`` are split on word boundaries.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    pieces: list[str] = []
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= chunk_size:
            pieces.append(paragraph)
        else:
            pieces.extend(_split_long_paragraph(paragraph, chunk_size))

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = f"{current}\n\n{piece}" if current else piece
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.append(current)
            overlap = _tail_on_word_boundary(current, chunk_overlap)
            current = f"{overlap}\n\n{piece}" if overlap else piece
        else:
            current = piece
    if current:
        chunks.append(current)

    return [Chunk(index=index, text=chunk) for index, chunk in enumerate(chunks)]


def _split_long_paragraph(paragraph: str, chunk_size: int) -> list[str]:
    """Split an oversized paragraph into word-boundary pieces of <= chunk_size."""
    pieces: list[str] = []
    current = ""
    for word in paragraph.split(" "):
        candidate = f"{current} {word}" if current else word
        if len(candidate) <= chunk_size or not current:
            current = candidate
        else:
            pieces.append(current)
            current = word
    if current:
        pieces.append(current)
    return pieces


def _tail_on_word_boundary(text: str, max_chars: int) -> str:
    """Return up to ``max_chars`` trailing characters, starting at a word boundary."""
    if max_chars == 0 or not text:
        return ""
    tail = text[-max_chars:]
    if len(tail) < len(text) and " " in tail:
        tail = tail.split(" ", 1)[1]
    return tail.strip()

"""Normalization of extracted document text before chunking."""

import re
import unicodedata

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SPACES = re.compile(r"[ \t]+")
_BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Normalize extracted text: unicode, line endings, whitespace.

    Keeps paragraph structure (double newlines) so the chunker can split
    on paragraph boundaries.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _CONTROL_CHARS.sub(" ", text)
    text = _SPACES.sub(" ", text)
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = _BLANK_LINES.sub("\n\n", text)
    return text.strip()

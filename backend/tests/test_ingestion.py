"""Unit tests for the knowledge ingestion pipeline (parsers, cleaner, chunker)."""

from pathlib import Path

import pytest

from app.ai.chunker import chunk_text
from app.ai.parsers import DocumentParseError, extract_text
from app.ai.text_cleaner import clean_text
from app.models.document import DocumentType


def build_pdf(text: str) -> bytes:
    """Build a minimal single-page PDF containing ``text``."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (number, obj)
    xref_position = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (
        len(objects) + 1,
        xref_position,
    )
    return bytes(out)


def build_docx(paragraphs: list[str], path: Path) -> None:
    import docx

    document = docx.Document()
    for paragraph in paragraphs:
        document.add_paragraph(paragraph)
    document.save(str(path))


class TestParsers:
    def test_txt(self, tmp_path: Path):
        path = tmp_path / "notes.txt"
        path.write_text("Visiting hours are 9 AM to 5 PM.", encoding="utf-8")
        assert extract_text(path, DocumentType.TXT) == "Visiting hours are 9 AM to 5 PM."

    def test_txt_latin1_fallback(self, tmp_path: Path):
        path = tmp_path / "notes.txt"
        path.write_bytes("Café hours".encode("latin-1"))
        assert "hours" in extract_text(path, DocumentType.TXT)

    def test_pdf(self, tmp_path: Path):
        path = tmp_path / "info.pdf"
        path.write_bytes(build_pdf("Cardiology OPD runs Monday to Friday."))
        assert "Cardiology OPD" in extract_text(path, DocumentType.PDF)

    def test_docx(self, tmp_path: Path):
        path = tmp_path / "info.docx"
        build_docx(["Emergency ward is open 24 hours.", "Dial 108 for ambulance."], path)
        text = extract_text(path, DocumentType.DOCX)
        assert "Emergency ward" in text
        assert "Dial 108" in text

    def test_corrupt_pdf_raises(self, tmp_path: Path):
        path = tmp_path / "broken.pdf"
        path.write_bytes(b"not a real pdf")
        with pytest.raises(DocumentParseError):
            extract_text(path, DocumentType.PDF)

    def test_empty_file_raises(self, tmp_path: Path):
        path = tmp_path / "empty.txt"
        path.write_text("   \n  ", encoding="utf-8")
        with pytest.raises(DocumentParseError):
            extract_text(path, DocumentType.TXT)


class TestTextCleaner:
    def test_normalizes_whitespace_and_line_endings(self):
        raw = "Line one\r\nLine   two\t\ttabbed\r\n\r\n\r\n\r\nLine three  "
        assert clean_text(raw) == "Line one\nLine two tabbed\n\nLine three"

    def test_strips_control_characters(self):
        assert clean_text("Hello\x00\x08World") == "Hello World"

    def test_preserves_paragraph_breaks(self):
        cleaned = clean_text("Para one.\n\nPara two.")
        assert cleaned.split("\n\n") == ["Para one.", "Para two."]


class TestChunker:
    def test_short_text_single_chunk(self):
        chunks = chunk_text("Small paragraph.", chunk_size=100, chunk_overlap=20)
        assert len(chunks) == 1
        assert chunks[0].index == 0
        assert chunks[0].text == "Small paragraph."

    def test_paragraphs_grouped_within_chunk_size(self):
        text = "\n\n".join(f"Paragraph number {i}." for i in range(10))
        chunks = chunk_text(text, chunk_size=80, chunk_overlap=10)
        assert len(chunks) > 1
        assert all(len(chunk.text) <= 80 for chunk in chunks)
        joined = " ".join(chunk.text for chunk in chunks)
        assert all(f"Paragraph number {i}." in joined for i in range(10))

    def test_long_paragraph_split_on_word_boundaries(self):
        text = " ".join(["word"] * 500)
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=0)
        assert all(len(chunk.text) <= 100 for chunk in chunks)
        assert all(not chunk.text.startswith(" ") for chunk in chunks)

    def test_adjacent_chunks_share_overlap(self):
        text = "\n\n".join(f"Sentence about topic {i}." for i in range(20))
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=40)
        first_tail = chunks[0].text[-30:]
        assert first_tail.split()[-1] in chunks[1].text

    def test_indexes_are_sequential(self):
        text = "\n\n".join(f"Paragraph {i}." for i in range(30))
        chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
        assert [chunk.index for chunk in chunks] == list(range(len(chunks)))

    def test_invalid_parameters_rejected(self):
        with pytest.raises(ValueError):
            chunk_text("text", chunk_size=0, chunk_overlap=0)
        with pytest.raises(ValueError):
            chunk_text("text", chunk_size=100, chunk_overlap=100)

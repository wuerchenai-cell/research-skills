"""Lightweight text extraction for study and reading tasks.

Extracts text from PDF, DOCX, TXT, and MD files.
PDF uses optional pypdf; DOCX uses optional python-docx.
If optional dependency is missing, returns a clear error.

For PDF, output preserves page boundaries as ``=== PAGE n ===`` markers
so evidence can be anchored to the original page.

Exit codes: 0 = extracted successfully,
1 = file missing / unsupported type / optional dependency missing,
2 = extraction failed (corrupt file, read error).
"""
from __future__ import annotations

import sys
from pathlib import Path


def extract_pdf(path: Path) -> tuple[str, str]:
    """Return (text, problem). Problem is empty when extraction succeeded."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return "", "PDF reading requires optional dependency pypdf. Install with: pip install pypdf"
    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        return "", f"PDF extraction failed: {exc}"
    text = "\n\n".join(
        f"=== PAGE {index} ===\n{text}" for index, text in enumerate(pages, start=1)
    )
    return text, ""


def extract_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"[ERROR] File not found: {path}"
    suffix = p.suffix.lower()
    if suffix in (".txt", ".md"):
        return p.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        text, problem = extract_pdf(p)
        if problem:
            return f"[ERROR] {problem}"
        return text
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError:
            return "[ERROR] DOCX reading requires optional dependency python-docx. Install with: pip install python-docx"
        doc = Document(str(p))
        return "\n".join(para.text for para in doc.paragraphs)
    return f"[ERROR] Unsupported file type: {suffix}"


def has_error(output: str) -> bool:
    return output.startswith("[ERROR]")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <file>", file=sys.stderr)
        sys.exit(1)
    output = extract_text(sys.argv[1])
    print(output)
    if has_error(output):
        sys.exit(2)

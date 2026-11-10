"""Lightweight text extraction for study and reading tasks.

Extracts text from PDF, DOCX, TXT, and MD files.
PDF uses optional pypdf; DOCX uses optional python-docx.
If optional dependency is missing, returns a clear error.
"""
from __future__ import annotations

import sys
from pathlib import Path


def extract_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"[ERROR] File not found: {path}"
    suffix = p.suffix.lower()
    if suffix == ".txt":
        return p.read_text(encoding="utf-8", errors="replace")
    if suffix == ".md":
        return p.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return "[ERROR] PDF reading requires optional dependency pypdf. Install with: pip install pypdf"
        reader = PdfReader(str(p))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError:
            return "[ERROR] DOCX reading requires optional dependency python-docx. Install with: pip install python-docx"
        doc = Document(str(p))
        return "\n".join(para.text for para in doc.paragraphs)
    return f"[ERROR] Unsupported file type: {suffix}"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <file>", file=sys.stderr)
        sys.exit(1)
    print(extract_text(sys.argv[1]))

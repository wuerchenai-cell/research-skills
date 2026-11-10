"""Incremental index of a folder (no original movement).

Usage: python index_folder.py <root> [--out index.csv]

Records filename, path, size, mtime, and a first-line title hint.
Skips already-indexed files whose size and mtime are unchanged by
reusing the previous title_hint from the existing index CSV.

Protected directories (.workbuddy, .git, __pycache__, etc.) are never
entered. Directory junctions, symlinks and other reparse points are
explicitly skipped (os.path.islink() is False for Windows junctions and
os.walk(followlinks=False) still descends into them), and every file's
resolved location is boundary-checked against the scan root before it
is read.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

EXTS = (".pdf", ".docx", ".txt", ".md", ".csv")
SKIP_DIRS = {"__pycache__", ".git", ".workbuddy", ".codex", ".ssh", ".aws", "node_modules"}


def title_hint(path: Path) -> str:
    try:
        if path.suffix.lower() in (".txt", ".md", ".csv"):
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.strip():
                    return line.strip()[:120]
        elif path.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            head = reader.pages[0].extract_text() or ""
            return head.splitlines()[0][:120] if head else ""
        elif path.suffix.lower() == ".docx":
            from docx import Document
            doc = Document(str(path))
            for para in doc.paragraphs:
                if para.text.strip():
                    return para.text.strip()[:120]
    except Exception:
        pass
    return ""


def _is_within(child: Path, parent: Path) -> bool:
    """True if child resolves to a path under parent (after link resolution)."""
    child = child.resolve()
    parent = parent.resolve()
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _is_reparse_or_link(path: Path) -> bool:
    """True for symlinks, junctions, and other reparse points.

    On Windows, ``os.path.islink()`` is False for junctions and
    ``os.walk(followlinks=False)`` still descends into them, so reparse
    points must be detected explicitly via ``os.lstat()`` and the
    ``st_reparse_tag`` stat field (Python 3.8+).
    """
    try:
        st = os.lstat(path)
    except OSError:
        return True  # cannot inspect -> treat as unsafe, do not enter
    if getattr(st, "st_reparse_tag", 0):
        return True
    return os.path.islink(path)


def _root_problem(root: Path) -> str:
    """Return a message when the scan root itself must not be scanned.

    Both the path as given and its resolved form are checked, so a root
    that reaches a protected directory through a junction or symlink is
    rejected as well.
    """
    candidates = [root]
    try:
        resolved = root.resolve()
    except OSError:
        return f"scan root path could not be resolved: {root}"
    if resolved != root:
        candidates.append(resolved)
    for cand in candidates:
        for part in cand.parts:
            if part.lower() in SKIP_DIRS:
                return f"scan root is inside a protected directory: {part}"
    return ""


def _safe_file(path: Path, root: Path) -> bool:
    """True only when the file's resolved location stays inside the scan
    root and outside protected directories (checked before any read)."""
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError):
        return False
    if not _is_within(resolved, root):
        return False
    return not any(part.lower() in SKIP_DIRS for part in resolved.parts)


def walk_protected(root: Path, out_path: Path) -> list[Path]:
    """Walk root without entering protected directories or following links.

    - Directory junctions/symlinks/reparse points are never descended
      into (explicitly filtered from ``dirnames``; on Windows junctions
      are invisible to ``os.path.islink`` and ``followlinks=False``).
    - File symlinks whose resolved target lies outside the scan root are
      skipped; every candidate's resolved location is boundary-checked
      against the scan root and protected directories before it is read.
    - Directory names are matched case-insensitively against SKIP_DIRS
      (Windows file systems are case-insensitive).
    - The index output file itself is excluded so it never indexes itself.
    """
    files: list[Path] = []
    out_resolved = out_path.resolve()
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # filter out protected directories and directory links in-place
        dirnames[:] = [
            d for d in dirnames
            if d.lower() not in SKIP_DIRS
            and not _is_reparse_or_link(Path(dirpath) / d)
        ]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() not in EXTS:
                continue
            if not _safe_file(p, root):
                continue
            try:
                if p.resolve() == out_resolved:
                    continue
            except (OSError, RuntimeError):
                continue
            files.append(p)
    return files


def load_existing_index(index_path: Path) -> dict[str, dict]:
    """Load previous index entries keyed by absolute path."""
    previous: dict[str, dict] = {}
    if not index_path.is_file():
        return previous
    try:
        with open(index_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                previous[row["path"]] = row
    except Exception:
        return previous
    return previous


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("--out", default="index.csv")
    args = parser.parse_args()
    root_arg = Path(args.root)
    if not root_arg.exists():
        print(f"[ERROR] root not found: {root_arg}", file=sys.stderr)
        sys.exit(1)
    problem = _root_problem(root_arg)
    if problem:
        print(f"[ERROR] {problem}", file=sys.stderr)
        sys.exit(1)
    root = root_arg.resolve()

    out_path = Path(args.out)
    previous = load_existing_index(out_path)

    files = walk_protected(root, out_path)
    rows: list[dict] = []
    reused = 0
    for path in files:
        stat = path.stat()
        key = str(path)
        prev = previous.get(key)
        if prev and int(prev["size"]) == stat.st_size and float(prev["mtime"]) == stat.st_mtime:
            # unchanged: reuse title_hint
            rows.append({
                "filename": path.name,
                "path": key,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "title_hint": prev["title_hint"],
            })
            reused += 1
        else:
            rows.append({
                "filename": path.name,
                "path": key,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "title_hint": title_hint(path),
            })
    rows.sort(key=lambda r: r["path"])
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "path", "size", "mtime", "title_hint"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] indexed {len(rows)} files -> {out_path} (reused {reused} unchanged)")


if __name__ == "__main__":
    main()

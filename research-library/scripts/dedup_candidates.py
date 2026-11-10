"""Suggest duplicate candidates by normalized title and full-content hash.

Usage: python dedup_candidates.py <root>

Computes a normalized title and a full-content SHA-256 hash for each file,
then reports files with matching hashes or similar titles. The hash covers
the whole file (streamed in blocks), so files that share only a common
prefix but differ at the tail are NOT reported as hash matches.

Does not delete or merge anything; candidates are suggestions only.

Protected directories (.workbuddy, .git, __pycache__, etc.) are never
entered. Directory junctions, symlinks and other reparse points are
explicitly skipped (os.path.islink() is False for Windows junctions and
os.walk(followlinks=False) still descends into them), and every file's
resolved location is boundary-checked against the scan root before it
is read or hashed.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

EXTS = (".pdf", ".docx", ".txt", ".md")
HASH_CHUNK = 1024 * 1024
SKIP_DIRS = {"__pycache__", ".git", ".workbuddy", ".codex", ".ssh", ".aws", "node_modules"}


def norm_title(name: str) -> str:
    title = Path(name).stem
    title = re.sub(r"[^A-Za-z0-9]+", " ", title)
    return re.sub(r"\s+", " ", title).strip().lower()


def file_hash(path: Path) -> str:
    """Full-content SHA-256, streamed in blocks (no prefix truncation)."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(HASH_CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


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


def _is_within(child: Path, parent: Path) -> bool:
    """True if child resolves to a path under parent (after link resolution)."""
    child = child.resolve()
    parent = parent.resolve()
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


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


def iter_files(root: Path) -> list[Path]:
    """Collect candidate files without entering protected directories or
    reparse points; only files whose resolved location stays inside the
    scan root are returned (checked before any read/hash)."""
    files: list[Path] = []
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [
            d for d in dirnames
            if d.lower() not in SKIP_DIRS
            and not _is_reparse_or_link(Path(dirpath) / d)
        ]
        for name in filenames:
            if Path(name).suffix.lower() not in EXTS:
                continue
            p = Path(dirpath) / name
            if not _safe_file(p, root):
                continue
            files.append(p)
    return files


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print("Usage: python dedup_candidates.py <root>", file=sys.stderr)
        sys.exit(1)
    root = Path(sys.argv[1])
    if not root.exists():
        print(f"[ERROR] root not found: {root}", file=sys.stderr)
        sys.exit(1)
    problem = _root_problem(root)
    if problem:
        print(f"[ERROR] {problem}", file=sys.stderr)
        sys.exit(1)
    files = iter_files(root)
    records = []
    for path in files:
        try:
            records.append((norm_title(path.name), file_hash(path), str(path)))
        except Exception:
            continue
    hash_groups: dict[str, list[str]] = {}
    title_groups: dict[str, list[str]] = {}
    for title, h, path in records:
        hash_groups.setdefault(h, []).append(path)
        title_groups.setdefault(title, []).append(path)
    for h, paths in hash_groups.items():
        if len(paths) > 1:
            print(f"[HASH MATCH] {h[:12]}:")
            for p in paths:
                print(f"  {p}")
    for title, paths in title_groups.items():
        if len(paths) > 1 and title:
            print(f"[TITLE MATCH] {title}:")
            for p in paths:
                print(f"  {p}")
    if len(records) == 0:
        print("[No files found]")


if __name__ == "__main__":
    main()

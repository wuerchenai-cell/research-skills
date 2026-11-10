"""Search notes (MD/TXT) by keyword.

Usage: python find_note.py <root> <keyword1> [keyword2 ...]

Protected directories (.workbuddy, .git, __pycache__, etc.) are never
entered. Directory junctions, symlinks and other reparse points are
explicitly skipped (os.path.islink() is False for Windows junctions and
os.walk(followlinks=False) still descends into them), and every file's
resolved location is boundary-checked against the scan root before it
is read.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

SKIP_DIRS = {"__pycache__", ".git", ".workbuddy", ".codex", ".ssh", ".aws", "node_modules"}


def _is_reparse_or_link(path: Path) -> bool:
    """True for symlinks, junctions, and other reparse points.

    On Windows, ``os.path.islink()`` is False for junctions and
    ``os.walk(followlinks=False)`` still descends into them, so reparse
    points must be detected explicitly via ``os.lstat()`` and the
    "st_reparse_tag" stat field (Python 3.8+).
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


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 3:
        print("Usage: python find_note.py <root> <keyword1> [keyword2 ...]", file=sys.stderr)
        sys.exit(1)
    root = Path(sys.argv[1])
    if not root.exists():
        print(f"[ERROR] root not found: {root}", file=sys.stderr)
        sys.exit(1)
    problem = _root_problem(root)
    if problem:
        print(f"[ERROR] {problem}", file=sys.stderr)
        sys.exit(1)
    keywords = [k.lower() for k in sys.argv[2:]]
    count = 0
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [
            d for d in dirnames
            if d.lower() not in SKIP_DIRS
            and not _is_reparse_or_link(Path(dirpath) / d)
        ]
        for name in filenames:
            if Path(name).suffix.lower() not in (".md", ".txt"):
                continue
            path = Path(dirpath) / name
            if not _safe_file(path, root):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace").lower()
            except Exception:
                continue
            hits = [k for k in keywords if k in text]
            if hits:
                print(f"{path}\t{','.join(hits)}")
                count += 1
    if count == 0:
        print("[No matching notes found]")


if __name__ == "__main__":
    main()

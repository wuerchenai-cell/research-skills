"""Bibliographic identity check with explicit verification levels.

Two distinct levels are reported:

  syntax     field-format check: title non-empty, DOI format, year format.
  existence  whether an authoritative record (Crossref) actually contains
             the title/year pair for the given DOI.

A syntax pass NEVER claims existence. When --authoritative is not used or
the network is unavailable, the result is reported as syntax-only /
unverified and must not be treated as evidence that the literature exists
or that its metadata matches.

Authoritative results report per-field outcomes (matched / mismatched /
unavailable). A field the authoritative record does not carry (e.g. no
issued year) is reported as unavailable, never as consistent. Overall:

  match      every supplied field matched the record.
  partial    record found, no mismatch, but at least one supplied field
             could not be verified (e.g. record has no year).
  mismatch   at least one supplied field differs from the record.
  unverified the authoritative lookup itself could not be performed.

Exit codes: 0 = pass (syntax-only, or authoritative match),
1 = syntax issues or authoritative mismatch,
3 = authoritative requested but unverified (network/record unavailable),
4 = partial verification (record found, some supplied fields unverifiable).

Usage:
  python identity_check.py --title "Title" --doi "10.xxxx/yyy"
  python identity_check.py --title "Title" --year 2022 --venue "IEEE TSP"
  python identity_check.py --title "Title" --doi "10.xxxx/yyy" --authoritative
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
YEAR_RE = re.compile(r"^\d{4}$")
CROSSREF_URL = "https://api.crossref.org/works/"
REQUEST_TIMEOUT = 10.0
TITLE_MATCH_RATIO = 0.9


def _norm_title(value: str) -> str:
    """Normalize a title for comparison.

    Unicode letters and digits are kept, so CJK titles do not collapse to
    the empty string (which used to make different Chinese titles compare
    as equal). Case is folded, NFKC folds full-width forms, and remaining
    punctuation/whitespace become single spaces.
    """
    text = unicodedata.normalize("NFKC", value or "")
    text = "".join(ch if ch.isalnum() else " " for ch in text.casefold())
    return re.sub(r"\s+", " ", text).strip()


def check_syntax(title: str, doi: str = "", year: str = "", venue: str = "") -> list[str]:
    """Field-format check only. Never claims the literature exists."""
    issues: list[str] = []
    if not title or not title.strip():
        issues.append("missing title")
    if doi:
        if not DOI_RE.match(doi):
            issues.append(f"DOI format looks invalid: {doi}")
    if year:
        if not YEAR_RE.match(year.strip()):
            issues.append(f"year looks invalid: {year}")
    if venue and not venue.strip():
        issues.append("empty venue")
    return issues


def verify_authoritative(title: str, doi: str, year: str = "",
                         timeout: float = REQUEST_TIMEOUT) -> dict:
    """Look up the DOI in Crossref and compare the fields the user supplied.

    Returns a dict with keys:
      status     one of ``match``, ``partial``, ``mismatch``, ``unverified``.
      fields     per-field outcome for every supplied field:
                 ``matched``, ``mismatched`` or ``unavailable``.
      checked    fields actually compared against the record (matched or
                 mismatched). Only ``matched`` fields may be claimed
                 consistent.
      unverified supplied fields that could not be compared (e.g. the
                 record carries no year). Never reported as consistent.
      problems   per-field mismatch / cannot-verify descriptions.
      record     the authoritative values found (title, year), for display.

    Authors, venue/journal and full-text claims are NEVER checked here; they
    are deliberately absent from ``checked`` and reported as not verified.
    """
    try:
        req = urllib.request.Request(
            CROSSREF_URL + doi,
            headers={"User-Agent": "research-find/identity-check (academic use)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "unverified", "fields": {}, "checked": [],
                "unverified": [], "problems": [], "record": {},
                "detail": f"authoritative lookup failed: {exc}"}

    message = payload.get("message", {}) if isinstance(payload, dict) else {}
    record_title = ""
    titles = message.get("title")
    if isinstance(titles, list) and titles:
        record_title = str(titles[0])
    record_year = ""
    issued = message.get("issued", {}).get("date-parts", [])
    if issued and issued[0]:
        # A None element means the record carries no usable year; keep it
        # empty so it is reported as unavailable, never compared as the
        # literal string "None".
        record_year = str(issued[0][0]) if issued[0][0] is not None else ""

    if not record_title:
        return {"status": "unverified", "fields": {}, "checked": [],
                "unverified": [], "problems": [], "record": {},
                "detail": "authoritative record has no title"}

    fields: dict[str, str] = {}
    problems: list[str] = []

    norm_user = _norm_title(title)
    norm_record = _norm_title(record_title)
    if not norm_user or not norm_record:
        # A title that normalizes to empty (e.g. symbols only) can never
        # count as a title match.
        fields["title"] = "unavailable"
        whose = "user title" if not norm_user else "authoritative record title"
        problems.append(
            f"title comparison unavailable: {whose} is empty after normalization"
        )
    elif difflib.SequenceMatcher(
        None, norm_user, norm_record
    ).ratio() >= TITLE_MATCH_RATIO:
        fields["title"] = "matched"
    else:
        fields["title"] = "mismatched"
        problems.append(f"title differs from authoritative record: '{record_title}'")

    if year:
        if record_year:
            if year.strip() == record_year:
                fields["year"] = "matched"
            else:
                fields["year"] = "mismatched"
                problems.append(
                    f"year {year} differs from authoritative record year {record_year}"
                )
        else:
            # The record carries no year: the user-supplied year stays
            # unverified and must not be reported as consistent.
            fields["year"] = "unavailable"
            problems.append(
                "year not verified: authoritative record carries no issued year"
            )

    checked = [f for f, s in fields.items() if s != "unavailable"]
    unverified = [f for f, s in fields.items() if s == "unavailable"]
    if "mismatched" in fields.values():
        status = "mismatch"
    elif unverified:
        status = "partial"
    else:
        status = "match"
    return {"status": status, "fields": fields, "checked": checked,
            "unverified": unverified, "problems": problems,
            "record": {"title": record_title, "year": record_year}}


def _describe_fields(result: dict) -> str:
    """Per-field summary that only claims fields actually compared."""
    fields = result.get("fields", {})
    record = result.get("record", {})
    parts = []
    if fields.get("title") == "matched":
        parts.append("title consistent with Crossref record")
    elif fields.get("title") == "mismatched":
        parts.append("title differs from Crossref record")
    elif fields.get("title") == "unavailable":
        parts.append("title could not be compared with the Crossref record")
    if fields.get("year") == "matched":
        parts.append(f"year {record.get('year')} consistent")
    elif fields.get("year") == "mismatched":
        parts.append(f"year differs from Crossref record year {record.get('year')}")
    elif fields.get("year") == "unavailable":
        parts.append("year not verified (authoritative record has no year)")
    message = "; ".join(parts) if parts else "nothing could be compared"
    unchecked = ["authors", "venue/journal", "full text"]
    return message + f"; not checked here: {', '.join(unchecked)}"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title")
    parser.add_argument("--doi")
    parser.add_argument("--year")
    parser.add_argument("--venue")
    parser.add_argument("--authoritative", action="store_true",
                        help="verify the DOI against Crossref (needs network)")
    parser.add_argument("--timeout", type=float, default=REQUEST_TIMEOUT)
    args = parser.parse_args()

    issues = check_syntax(args.title or "", args.doi or "", args.year or "", args.venue or "")
    if issues:
        for issue in issues:
            print(f"[WARN] syntax: {issue}")
        print("[NOT CHECKED] authoritative verification not attempted")
        sys.exit(1)
    print("[OK] syntax: identity fields present and format-plausible")

    if not args.authoritative:
        print("[UNVERIFIED] syntax-only; this does NOT confirm the literature exists "
              "or that the metadata matches")
        print("[HINT] rerun with --authoritative for existence verification via Crossref")
        sys.exit(0)

    if not (args.doi or "").strip():
        print("[UNVERIFIED] --authoritative requires --doi")
        sys.exit(3)
    result = verify_authoritative(args.title or "", args.doi, args.year or "",
                                  timeout=args.timeout)
    status = result["status"]
    if status == "match":
        print(f"[VERIFY] authoritative match: {_describe_fields(result)}")
        sys.exit(0)
    if status == "partial":
        print(f"[PARTIAL] authoritative record found, but not everything could be "
              f"verified: {_describe_fields(result)}")
        sys.exit(4)
    if status == "mismatch":
        problems = "; ".join(result["problems"])
        compared = ", ".join(result["checked"]) if result["checked"] else "nothing"
        print(f"[MISMATCH] authoritative mismatch (fields compared: {compared}): {problems}")
        print(f"[MISMATCH] field summary: {_describe_fields(result)}")
        sys.exit(1)
    print(f"[UNVERIFIED] {result.get('detail', 'authoritative verification unavailable')}")
    sys.exit(3)


if __name__ == "__main__":
    main()

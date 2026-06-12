"""Normalization rules for legacy data.

Every rule here exists because the raw data violated it — see
docs/TESTING_NOTES.md and data/legacy_rescue for provenance. Tests in
tests/test_ingest_normalize.py are the executable quirk ledger.
"""

import re

# Topic names arrive with tree-depth prefixes of MINUS SIGN (U+2212) or
# hyphens; categories arrive SHOUTING with stray whitespace.
_DEPTH_PREFIX = re.compile(r"^[\s−\-]+")  # noqa: RUF001 — U+2212 is what the data contains
_WHITESPACE = re.compile(r"\s+")


def clean_text(value):
    """Strip NUL bytes (present in legacy descriptions; PostgreSQL rejects
    them, SQLite silently tolerated them)."""
    return (value or "").replace("\x00", "")


def clean_name(value):
    """Collapse internal whitespace and strip — fixes 'Christian LIfe '-style
    near-duplicates born of trailing/double spaces."""
    return _WHITESPACE.sub(" ", clean_text(value).strip())


def clean_topic_name(value):
    """Topic names additionally carry depth prefixes (U+2212 minus signs or
    hyphens) from the legacy dropdown rendering."""
    return clean_name(_DEPTH_PREFIX.sub("", value or ""))


def clean_year(value):
    """Series year fields hold free text (e.g. '18--2,2'); keep only a clean
    4-digit year, else empty."""
    match = re.search(r"\b(19|20)\d{2}\b", str(value or ""))
    return match.group(0) if match else ""


def is_livestream_name(name):
    """Legacy convention: livestreams are titled 'LIVE STREAM - ...'.
    'NO LIVE STREAM' announcements are not livestreams."""
    upper = (name or "").upper()
    return "LIVE STREAM" in upper and not upper.startswith("NO LIVE STREAM")


def detect_platform(url):
    if "vimeo.com" in url:
        return "vimeo"
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    return "other"

"""The executable quirk ledger — every rule earned by real legacy data."""

from catalogue.ingest.normalize import (
    clean_name,
    clean_topic_name,
    clean_year,
    date_from_ref,
    detect_platform,
    is_livestream_name,
)


def test_date_from_ref_recovers_dates_the_admin_left_blank():
    # The programmeRef encodes DD.MM.YY even when the date field is empty —
    # 45 such programmes found in the 2026-06 backfill.
    assert date_from_ref("MD8280CINews25.10.24") == "2024-10-25"
    assert date_from_ref("1MD8142SDF13.07.25") == "2025-07-13"
    assert date_from_ref("YT6336SermonPM31.05.26") == "2026-05-31"


def test_date_from_ref_rejects_non_dates():
    assert date_from_ref("YT6325KidsTalk") is None  # no DD.MM.YY group
    assert date_from_ref("REF99.99.99") is None  # impossible day/month
    assert date_from_ref("MD8201.13.25") is None  # month 13
    assert date_from_ref("") is None
    assert date_from_ref(None) is None


def test_clean_name_collapses_the_whitespace_that_made_duplicates():
    assert clean_name("Redfearn, Jonathan ") == "Redfearn, Jonathan"
    assert clean_name("Christian  Life") == "Christian Life"
    assert clean_name(None) == ""


def test_clean_topic_name_strips_dropdown_depth_prefixes():
    assert clean_topic_name("−−− The Sovereignty of God") == "The Sovereignty of God"  # noqa: RUF001
    assert clean_topic_name("--- Prayer") == "Prayer"


def test_clean_topic_name_strips_mojibake_depth_prefix():
    # The depth-marker MINUS SIGN (U+2212) double-encoded: UTF-8 bytes E2 88 92 read
    # as Latin-1 → U+00E2 U+0088 U+0092. Real data: "The Grace of God".
    mojibake = "âââ The Grace of God"
    assert clean_topic_name(mojibake) == "The Grace of God"
    # A name legitimately starting with â must NOT be stripped.
    assert clean_topic_name("âccent on grace") == "âccent on grace"
    assert clean_topic_name("Apologetics") == "Apologetics"


def test_clean_year_extracts_real_years_from_free_text():
    assert clean_year("2018") == "2018"
    assert clean_year("18--2,2") == ""
    assert clean_year("Easter 2021 series") == "2021"
    assert clean_year(None) == ""


def test_livestream_naming_convention():
    assert is_livestream_name("LIVE STREAM - 6.30pm Service") is True
    assert is_livestream_name("NO LIVE STREAM - Evening 6.30pm") is False
    assert is_livestream_name("Romans 8 - Sermon") is False


def test_platform_detection():
    assert detect_platform("https://vimeo.com/97323692") == "vimeo"
    assert detect_platform("https://www.youtube.com/watch?v=abc") == "youtube"
    assert detect_platform("https://example.com/video.mp4") == "other"


def test_clean_text_strips_nul_bytes_that_postgres_rejects():
    from catalogue.ingest.normalize import clean_text

    assert clean_text("Sermon\x00 notes") == "Sermon notes"
    assert clean_name("Speaker\x00 Name ") == "Speaker Name"

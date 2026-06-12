"""The executable quirk ledger — every rule earned by real legacy data."""

from catalogue.ingest.normalize import clean_name, clean_topic_name, clean_year, detect_platform, is_livestream_name


def test_clean_name_collapses_the_whitespace_that_made_duplicates():
    assert clean_name("Redfearn, Jonathan ") == "Redfearn, Jonathan"
    assert clean_name("Christian  Life") == "Christian Life"
    assert clean_name(None) == ""


def test_clean_topic_name_strips_dropdown_depth_prefixes():
    assert clean_topic_name("−−− The Sovereignty of God") == "The Sovereignty of God"  # noqa: RUF001
    assert clean_topic_name("--- Prayer") == "Prayer"
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

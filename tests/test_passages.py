"""Passage parsing, tested against the real title patterns observed in the
catalogue (see the per-book title samples in the Epic 6.6 session)."""

import pytest

from catalogue.passages import parse_passage, passage_label


@pytest.mark.parametrize(
    "title,book,expected",
    [
        ("Luke 20:9-19 - If I Were God - JPC Service", "Luke", {"chapter": 20, "verse_start": 9, "verse_end": 19}),
        (
            "Romans 12: 1-13 - Queen's Jubilee - JPC Sermon",
            "Romans",
            {"chapter": 12, "verse_start": 1, "verse_end": 13},
        ),
        ("Luke 19: 10 - Jesus Came to Save - JPC Sermon", "Luke", {"chapter": 19, "verse_start": 10, "verse_end": 10}),
        (
            "1 Samuel 12 - Here I Stand - JPC Sermon",
            "1 Samuel",
            {"chapter": 12, "verse_start": None, "verse_end": None},
        ),
        (
            "1 Samuel 18-19 - David and Saul - JPC Sermon",
            "1 Samuel",
            {"chapter": 18, "verse_start": None, "verse_end": None},
        ),
        (
            "Psalm 95 - The Reformation Revelation - JPC Sermon",
            "Psalms",
            {"chapter": 95, "verse_start": None, "verse_end": None},
        ),
    ],
)
def test_parses_real_sermon_title_patterns(title, book, expected):
    assert parse_passage(title, book) == expected


def test_topical_titles_do_not_match():
    assert parse_passage("Word Alive '10 - Peter Baker: A Song of Revelation", "Psalms") is None
    assert parse_passage("Keswick '10 - Alistair Begg 1: Bible Reading", "Romans") is None
    assert parse_passage("Ask Phillip - Given the Holy Spirit Twice?", "Luke") is None


def test_song_of_solomon_variants():
    assert parse_passage("Song of Songs 2 - Love", "Song of Solomon")["chapter"] == 2
    assert parse_passage("Song of Solomon 1:1 - Intro", "Song of Songs")["chapter"] == 1


def test_passage_label_formats():
    assert passage_label({"chapter": 12, "verse_start": 1, "verse_end": 13}) == "12:1-13"
    assert passage_label({"chapter": 19, "verse_start": 10, "verse_end": 10}) == "19:10"
    assert passage_label({"chapter": 95, "verse_start": None, "verse_end": None}) == "95"
    assert passage_label(None) is None

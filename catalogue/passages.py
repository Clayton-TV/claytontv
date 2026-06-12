"""Parse a Bible passage from a video title.

Clayton TV's sermon titles overwhelmingly lead with the passage —
"Luke 20:9-19 - ...", "1 Samuel 18-19 - ...", "Psalm 95 - ..." — so a
chapter is recoverable for most expository teaching (conference talks, which
are topical, simply don't match, which is correct). Used to order and group
a book's teaching by chapter and to build the chapter-navigation strip.
"""

import re

# Book display names whose titles use a different word, or a singular form.
_NAME_VARIANTS = {
    "Psalms": ["Psalms", "Psalm"],
    "Song of Solomon": ["Song of Solomon", "Song of Songs", "Song of Sol"],
    "Song of Songs": ["Song of Songs", "Song of Solomon"],
}


def variants(book_display_name):
    return _NAME_VARIANTS.get(book_display_name, [book_display_name])


def parse_passage(title, book_display_name):
    """Return {chapter, verse_start, verse_end} for a title that opens with this
    book's passage, else None. chapter is an int; verses may be None."""
    if not title:
        return None

    for name in variants(book_display_name):
        # <book> <chapter>[-<chapter2>][:|. <v1>[-<v2>]] at the start of the title
        pattern = re.compile(
            rf"^\s*{re.escape(name)}\s+(\d+)(?:\s*-\s*\d+)?(?:\s*[:.]\s*(\d+)(?:\s*-\s*(\d+))?)?",
            re.IGNORECASE,
        )
        match = pattern.match(title)
        if match:
            chapter = int(match.group(1))
            verse_start = int(match.group(2)) if match.group(2) else None
            verse_end = int(match.group(3)) if match.group(3) else verse_start
            return {"chapter": chapter, "verse_start": verse_start, "verse_end": verse_end}
    return None


def passage_label(passage):
    """'12:1-13' / '12:1' / '12' from a parsed passage."""
    if not passage:
        return None
    chapter = str(passage["chapter"])
    if passage["verse_start"] is None:
        return chapter
    if passage["verse_end"] and passage["verse_end"] != passage["verse_start"]:
        return f"{chapter}:{passage['verse_start']}-{passage['verse_end']}"
    return f"{chapter}:{passage['verse_start']}"

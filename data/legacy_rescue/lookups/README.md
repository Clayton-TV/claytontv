# Legacy admin lookup tables (captured 2026-06-12)

The ID→name maps for speakers, topics, bible books, and series, read from the
legacy admin's `<select>` dropdowns on `mediaProgrammeMeta.asp` (i2i Media "The
Internet Broadcaster", channel 16) during an authenticated, **read-only**
browser session. The ClayScraper only ever captured the numeric `id|0`
references on each programme, never these name tables — so this is the missing
half that makes scraped programme data resolvable to real speaker/topic/book
names.

| File | Rows | Notes |
|---|---|---|
| speakers.csv | 697 | `legacy_id,name` — "Surname, First" form |
| topics.csv | 152 | hierarchical; sub-topics prefixed `−−−` (U+2212), categories in CAPS |
| books.csv | 67 | 66 canon + a duplicate ("Song of Solomon" id 22 / "Song of Songs" id 67) |
| series.csv | 2549 | hierarchical; depth encoded by leading `-` dashes |

## Quirks found (feed Epic 2 importer tests)
- **Duplicate "Education" topic** (ids 108 and 169) — matches the special-case
  already hardcoded in ctvDBreform's mapper.csv. Confirms the dedup logic the
  new importer needs.
- Topic/series names carry their tree depth as a text prefix, not as structured
  parent IDs — the hierarchy must be reconstructed from the indentation.
- Speaker references in scraped data are `id|0` pairs; the `|0` suffix is a
  constant the scraper preserved. Join on `legacy_id`.

## Provenance
Source: dropdown options on the authenticated admin meta page. No write/edit/
submit actions were performed — navigation and DOM reads only. The numeric IDs
are the legacy primary keys, stable across the scraper sequence.

# Integration testing notes

Findings from in-browser test sessions against the local staging environment
(`https://claytontv.test`, Herd proxy → Django on :8000, full legacy CSV import:
9,244 videos / 1,070 series / 693 speakers). Each finding is tagged with the
epic that owns the fix.

## 2026-06-12 — first full-catalogue session (desktop + mobile)

**Fixed during session**
- ✅ Vimeo unlisted embeds: 2,443/4,543 legacy Vimeo URLs carry a privacy hash
  (`vimeo.com/<id>/<hash>`) that the embed builder dropped → "Sign in to Vimeo"
  wall. Now passed through as `?h=`. Commit `b0bf8db`.

**Data quirks (Epic 2 — import pipeline)**
- Duplicate near-identical topics: "Christian Life" and "Christian LIfe" both
  exist as chips on the homepage. Same family as the duplicate-ministry
  whitespace issue in #86 — add normalization + dedup to the upsert importer.
- Mangled comma-concatenated series names, e.g.
  `'Series '10 - Judges, Acts, Colossians, Psalms , Living Life to the Full,The
  Grace of Giving` (stray leading apostrophe, comma-joined multi-series). The
  comma-delimiter problem of #88 at series level.
- ✅ FIXED — "0 programmes" on every series: the homepage counted Count("video")
  (the Video.series FK, never populated by the importer) instead of
  Count("videos") (the Series.videos M2M that link_series writes). Real counts
  now show; empty series dropped.
- ✅ FIXED — `is_livestream` False for all videos: import_videos had the
  IsLivestream column commented out. Uncommented, plus an idempotent
  backfill_livestream_flags command. **Deploy note:** run
  `backfill_livestream_flags` on beta after deploys until the Epic 2 importer
  rework lands (code deploy ships the fix, not the data update).
- ~230 video IDs skipped on import (matches #86's "mostly unlisted, acceptable").
- Topic `category` values have near-duplicate variants: "CHRISTIAN LIFE"
  appears as two distinct groups on /topic (whitespace/case variant) —
  normalize in the importer.
- Series `year_start`/`year_end` hold free text (e.g. "18--2,2"); the series
  page guards display, but the importer should clean these to real years.
- Some hashless Vimeo videos (e.g. video 749, Keswick '12) show a genuine
  Vimeo sign-in wall — privacy setting on the video itself, not our embed code.
  Needs the Vimeo account audit (Ettie question).

**UX findings**
- Mobile (375 px): content column overflows to ~440 px → horizontal scroll on
  the homepage. Known territory (#162, Jonathan's WIP branch). (Epic 6)
- Watch page metadata shows placeholder fallbacks ("Speaker Name", "00:00")
  when data is missing — fine for dev, not for congregants. (Epic 6, #163
  empty states)
- Search works well at 9k-video scale via ORM, including category results.
  Typesense (Epic 5) still wanted for typo-tolerance + transcript search.

**Testing methodology**
- The Chrome-extension full-page screenshot sometimes renders cross-origin
  iframes (YouTube/Vimeo players) as black. Use the `zoom` capture on the
  player region to verify embeds — it captures true pixels. The Claude Preview
  panel is more reliable for responsive-viewport testing than resizing the
  real Chrome window.

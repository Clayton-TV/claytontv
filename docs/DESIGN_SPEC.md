# Design specification — functionality & behaviour

> Living document. The test for every page: **name the single question it
> answers, for whom**. If a page cannot name its question, it is a database
> index wearing a UI — redesign or kill it. (Lesson learned twice: the
> 1,069-series homepage dump, then the 662-speaker A–Z directory.)

## Personas

| | Who | Arrives wanting |
|---|---|---|
| P1 | Elderly congregant | "Watch this Sunday's service" / "catch up on what I missed" — two taps, large targets, zero jargon |
| P2 | Explorer/seeker | "What is this site? Is there something for me?" — orientation, trust signals, a safe first click |
| P3 | Student / minister / group leader | "Find teaching on Romans 8 / prayer / by this speaker; prep my small group" — precision, depth, speed |
| P4 | Parent | "Something trustworthy for my kids" — one obvious path, confidence |
| P5 | Editor (Ettie/delegates) | Curate content quickly without breaking things — admin, not public UI |

## Three retrieval modes (and the rule)

1. **Known-item lookup** — "do you have X?" → *search-first* UI (instant,
   typo-tolerant; Epic 5 Typesense). Never make a human scan a list for a
   name they can type.
2. **Discovery** — "what should I watch?" → *curation-first* UI (featured,
   weighted by catalogue depth and recency; small numbers, strong scent).
3. **Reference traversal** — "more like the thing I'm looking at" → *detail
   pages as destinations* (speaker page, series page, topic page) reached by
   chips from content, not by browsing an index.

**The rule:** index pages are routers between these modes, never the
destination. Detail pages are the destinations. Long tails are collapsed
behind lookup, not paginated A–Z.

## Page-by-page specification

### Home — "What is this, and what should I watch right now?" (P1, P2)
Shipped: hero + next-service slot, latest, featured series, topics (scroll-
deferred). **To add:** real broadcast state (E4); *Continue watching* row
(localStorage progress — see cross-cutting); audiences entry point for P4.
Pattern: Laracasts home / Netflix rows, stripped to one screen of intent.

### Watch — "Play this. What is it? What's next?" (all)
Shipped: player, metadata chips, deferred series rail. **To add:**
- *Resume position* + "watched" state (localStorage)
- **Share** — native share sheet / copy link / WhatsApp: forwarding sermons
  is THE growth loop in church culture; make it one large obvious button
- Series position ("Part 3 of 8") — needs `number_in_series` (Epic 2)
- Related resources links (rescued printandaudio/desiringgod mapping, Epic 2)
- Transcript pane with click-to-seek (E4 captions + E5 index) — flagship
- "Report a problem" (#83) — tiny, builds trust
Pattern: YouTube watch page hierarchy; Laracasts lesson page for series
context.

### Series index — "What teaching journeys exist?" (P2, P3)
Shipped: filterable card grid, most-episodes-first. **To improve:** facet by
ministry; sort newest/biggest; **cover images derived from first episode's
thumbnail** (no new data needed — Epic 2 derivation). Pattern: Laracasts
courses grid.

### Series detail — "Should I commit? Where do I start?" (P2, P3)
Shipped: course header + episode grid. **Redesign behaviours:**
- Episodes as **ordered list rows** (number, title, duration, watched tick),
  not a card grid — lists scan; grids browse. Needs `number_in_series` +
  durations (Epic 2/E4)
- "Start with episode 1" primary CTA; "Continue from ep. N" when localStorage
  knows
- Attribution row (speaker(s), ministry, years)
Pattern: Laracasts course page — this is the page the whole "courses" vision
hangs on.

### Topics index — "Browse by what's on my heart" (P2, P3)
Shipped: grouped chips + audiences. Good shape. Epic 2 fixes the duplicate
"CHRISTIAN LIFE" group. Consider later: one featured video per area as scent.

### Topic detail — "Best teaching on prayer?" (P3, P2)
Currently a generic date-ordered grid. **Needs:** sort (recent ↔ most
relevant), filter by audience and format; series-level results mixed with
talks ("the Prayer series" beats 40 loose talks). Pattern: YouTube filter
bar, kept to two controls.

### Speakers index — REDESIGN (the page that prompted this spec)
Question it must answer: "Whose teaching should I explore?" (P2/P3) and
"do you have X?" (P3 → lookup).
- **Lookup-first**: the filter box becomes the hero — type a name, instant
- **Featured voices**: a curated tier — speakers with deep catalogues
  (weight = talk count × recency), shown faculty-style with photo + bio
  (both fields exist in the model, unused!) + "best known for <series>"
- **Long tail collapsed**: "All speakers A–Z" as a compact, scroll-deferred
  (WhenVisible) plain-text column list — present for completeness, not
  pretending to be content
Pattern: a seminary "faculty" page / Laracasts instructors — except they have
20 and we have 662, hence the two-tier split.

### Speaker detail — "More from this voice" (P3, P2) — the REAL destination
Currently a generic Browse grid. **Redesign:** bio header (photo, bio,
ministry affiliation), their **series first** (grouped), then loose talks;
share button. Needs: speaker thumbnail/bio data audit (Epic 2 — fields exist,
fill rate unknown).

### Bible books index — "Teaching on scripture, the way I think of it" (P3)
Shipped: canonical order, section groups, dimmed empty books. Right shape.

### Bible book detail — "Teaching on Romans" (P3)
Generic grid today. **High-value derivation (Epic 2): parse chapter/verse
from video titles** ("Romans 8:1-17 — ..." patterns are pervasive) → order
teaching by passage, show a chapter strip (Rom 1 2 3 … 16) as filter. Novel
for this niche, enormous value for P3; no other church platform does it well.

### Ministries index/detail — "My church / an org I trust" (P1, P2)
Index shipped. Detail: header + their series + latest. Channels (provenance)
fold into ministry pages as "where they publish" (Epic 2/3).

### Latest — "What's new since Sunday?" (P1 weekly returner, P2 explorer)
~~Keep as is~~ — superseded (June 2026): a flat paginated wall answers no
one's question. Becomes a **feed with a spine**:
- Group by time, editorially: "This week" / "Last week" / "Earlier in June" —
  people think "two Sundays ago", never "page 3".
- Collapse series floods: 4 livestreams from one series = one series row
  ("4 new in *Romans*"), not four near-identical cards.
- "New since your last visit" divider from a localStorage timestamp — quiet
  rule line; pairs with watched ticks, still no accounts.
- Facet chips (speaker / ministry / talks-vs-streams) via partial reloads.

### Past live streams — becomes **Services** when E4 lands (live state +
schedule + archive in one page). Defer redesign to E4.

### Search — the connective tissue (all personas)
Today: icontains + page. **E5 target:** header field becomes instant overlay
(results as you type, grouped videos/series/speakers/topics, keyboard nav,
⌘K); **transcript hits with timestamp deep-links** (E4+E5) — the flagship
P3 feature. Pattern: Algolia DocSearch interaction grammar.

## Cross-cutting behaviours

| Behaviour | Personas | Effort | Notes |
|---|---|---|---|
| Continue watching / watched ticks | P1, P3 | S | localStorage only — **no accounts needed**; sidesteps the auth scope question entirely |
| Share (native sheet, copy, WhatsApp) | P1! | S | The church growth loop; large target on watch page |
| Live/next-service state | P1 | M | E4; powers home slot + Services page |
| Transcript search & click-to-seek | P3 | L | E4 captions + E5 index; flagship |
| Passage parsing from titles | P3 | M | Epic 2 derivation; chapter strips on book pages |
| Audience (kids) pathway | P4 | S | Audiences group shipped; consider persistent toggle later |
| Text-size control (#23) | P1 | S | 6.8 with the a11y audit |
| Report a problem (#83) | trust | S | watch page footer |
| Empty/error states with next actions | all | S | 6.8 |

## Connected app layer (June 2026)

The destination pages made good reading rooms; this layer makes them one
app. The load-bearing fact: our Inertia setup uses **persistent layouts**
(resources/js/app.ts) — AppLayout never remounts across navigations, so
things mounted there survive page changes. Everything below is invisible
until invoked: the calm elderly-first surface stays calm; depth is for P3.

1. **Player API layer — the keystone.** `usePlayer` composable wrapping the
   YouTube iframe API + Vimeo player SDK (both postMessage). Unlocks in one
   stroke: true resume positions, watched-at-80% (replaces watched-on-open),
   autoplay-next (series become real playlists), keyboard playback control,
   mini-player scrubbing. Build first; everything else hangs off it.
2. **Persistent mini-player.** The iframe lives in AppLayout at fixed
   position; the watch page renders a placeholder the player positions over
   (a moved iframe reloads; a repositioned one doesn't). Navigate away →
   player animates to bottom corner: scrub bar, title, next, close,
   maximize-returns-to-watch. The minimize transition is motion-as-
   information: it tells you the video kept playing. Laracasts feel; right
   for long-form audio-led teaching.
3. **Command palette + global shortcuts.** Header search expands to a
   centre-screen ⌘K modal (shadcn-vue `Command`): fuzzy search across
   videos/series/speakers/books/topics + actions ("Resume: …"). Shortcuts
   (only when not typing): ⌘K, `/`, space, ←/→ ±10s, m, f, esc minimize,
   n next-in-series, ? help sheet.
4. **Transcript embeddings — the 100x.** Rescued transcripts → sentence-
   transformers → pgvector: semantic search over *what was said* ("anxiety"
   finds the sermon that never used the word), genuinely-related videos,
   palette answers. Separate backend epic; the P3 reason-to-use-the-site.

Order: Latest regroup → player API → palette/shortcuts → mini-player →
embeddings (parallel backend track).

## Data the designs are waiting on (feeds Epic 2's importer rework)

1. `number_in_series` (legacy dump has NumbInSeries — currently dropped)
2. Durations (YouTube API E4; Vimeo oEmbed for the rest)
3. Speaker bio/photo fill-rate audit (model fields exist)
4. Series cover = first episode thumbnail (derivation)
5. Chapter/verse parsed from titles (derivation)
6. Dedup/normalization: topics ("Christian LIfe"), categories ("CHRISTIAN
   LIFE " variant), Education ids 108/169, book 22/67, year fields
7. Related-resources mapping (rescued, data/legacy_rescue)
8. The ~1,670 programmes added since the dump (incremental sync)

## Sequencing

1. **Epic 2 importer rework now** — six of eight design dependencies above
   are data work; the redesigns starve without it.
2. **6.6 "destinations" round**: speaker detail, series detail v2, book
   detail with passage strip, speakers index pivot — in that order (each is
   useful the day it ships).
3. **E4 + E5** unlock Services, transcript search, durations.
4. **6.7 motion / 6.8 light mode + a11y** close the epic.

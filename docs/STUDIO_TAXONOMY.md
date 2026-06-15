# Studio — taxonomy management (Slice 6) — exploration doc

**Status:** discussion doc, not a build spec. For the team to react to before we
commit to anything. The Django `/admin` already covers rename / merge / edit for
the rare manual case, so this is genuinely low-priority — the question is whether
a nicer assisted flow is worth building, and if so, what shape.

Slices 0–5 of the Studio are done & live on beta (intake single + bulk +
playlist → library → editor → review → publish, with recoverable soft-delete).
Slice 6 is the last sketched piece: **rename / merge duplicate speakers (and
topics), and edit series/topic summaries.**

---

## What the data actually says (local imported catalogue, 2026-06-15)

Before designing anything, the load-bearing question was *"is the duplicate list
a long table or a short one?"* It's **short.**

| Metric | Speakers |
| --- | --- |
| Total speakers | **695** |
| Speakers with 0 videos (orphans) | **31** |
| Exact name-variant duplicates (token-set match, e.g. "Last, First" vs "First Last") | **0** |
| Fuzzy near-match candidate **pairs** ≥ 0.82 similarity | **8** |
| …of those, ≥ 0.92 (very likely dups) | **2** |

The top fuzzy candidates (similarity · name · video-count):

```
0.96  Noll, Stephen (1)      ~  Knoll, Stephen (1)        ← likely a typo dup
0.93  Williams, Peter (4)    ~  Williams, Peter J (10)    ← likely same person
0.90  Williams, Gary J (1)   ~  Williams, Garry (4)       ← likely same person
0.87  Pearson, Andrew (1)    ~  Patterson, Andrew (1)     ← probably DIFFERENT
0.86  Thompson, Martin (4)   ~  Thompson, Mark (2)        ← DIFFERENT people
0.85  Chin, Richard (1)      ~  Coekin, Richard (12)      ← DIFFERENT (false +)
0.85  Earnshaw, Zoe (4)      ~  Earnshaw, Rod (144)       ← DIFFERENT (married?)
```

**Takeaways:**
1. **Volume is tiny.** A handful of candidate pairs, not hundreds. A single
   tick-list table is completely fine — no pagination/scale worry.
2. **The hard part is judgment, not finding them.** "Peter Williams" vs "Peter J
   Williams" — same person? Most false positives are real, distinct preachers
   who happen to share a surname or first name. So the value of any tool is in
   **helping a human decide**, not in the matching itself.
3. **Series duplicates are largely already handled** — Epic 2 pruned orphan and
   identical-twin series. Series here is mostly about **editing summaries**, not
   merging.
4. Worth a quick separate sweep: the **31 orphan speakers** (0 videos) are safe
   cleanup candidates regardless of the merge question.

> Numbers are from the local import; beta/prod will be in the same ballpark.
> Re-run the analysis there before acting (the snippet is in the PR description).

---

## The three jobs, by difficulty

| Job | Difficulty | Notes |
| --- | --- | --- |
| **Edit summaries** (series, topic) | Easy | Just editing a text field — same pattern as the video editor's Save. Genuinely useful (course/series pages show these). |
| **Rename** a speaker/topic | Easy | Edit `name`; re-index affected videos. |
| **Merge** two records into one | Medium / careful | The only fiddly bit — see below. |

### Merge mechanics (the careful bit)
Merging "loser" → "winner" means:
- Re-point every video from loser to winner across the **correct** relation —
  speakers via the `Video.speaker` M2M, but **series via `Series.videos`** (the
  per-model quirk that's bitten us before). De-dupe the join so a video linked to
  both doesn't end up doubled.
- Re-index all affected videos in search (the live signal handles per-video saves).
- **Soft-delete** the loser (we have `deleted_at` now) rather than hard-delete —
  so a bad merge is recoverable.
- Confirmation UI must state the blast radius: "Merge 4 videos from *Peter
  Williams* into *Peter J Williams*. The first record is moved to trash."

---

## Ideas to explore — assessing "is this a duplicate?"

The point of the tool is to make the *judgment* fast and safe. Options, roughly
cheapest → richest:

### A. Candidate detection ("automatic research", local/free)
- **Fuzzy name match** (what the table above uses) to *suggest* pairs. Cheap,
  already prototyped.
- **Shared-context signals** — the strongest tell. Two records are very likely
  the same person if they share a **series, channel, topic, or Bible book**, or
  overlap in date range. Surfacing "these two both appear in *Galatians @ St
  Helen's*" is often more convincing than the name similarity.

### B. Assisted-decision UI
- **Tick-list table** of candidate pairs (feasible — it's short): each row shows
  both names, video counts, shared-context signals, a similarity score, and
  actions: **Merge** · **Not a duplicate** (dismiss so it never reappears) ·
  **Open both**.
- **Side-by-side compare panel** when assessing a pair: each side lists its
  videos, series, channels, thumbnails/photos — so the human can eyeball "yep,
  same preacher" in seconds.
- **Dismissed-pairs memory** so "Thompson, Martin ≠ Thompson, Mark" stays
  resolved and the list keeps shrinking.

### C. AI / web "research" (optional, richer)
- An LLM judgment: "Are *J. Smith* and *John Smith*, who both preach at St
  Helen's Bishopsgate, the same person? Reply same / different / unsure with a
  reason." Ties into **Direction D** (the local Ollama PoC) — keeps it free and
  private.
- Light web lookup to confirm a speaker's identity / canonical name / a bio +
  photo (which would *also* enrich the speaker page, not just dedup).
- **Caveat:** confidence, not truth. Always a human tick to confirm; AI only
  ranks/sorts the list and drafts a rationale.

---

## Open questions for the group
1. Is this worth building now, or does `/admin` + the short list mean we **defer**
   until beta-tester usage shows real pain?
2. Which taxonomies need **merge** vs just **rename/edit**? (Proposal: merge for
   speakers only; rename + summary-edit for topics/series.)
3. How much "automatic research" do we want in v1 — just fuzzy + shared-context
   signals (cheap, probably enough), or pull in the AI/web angle (richer, more
   work, overlaps Direction D)?
4. Do we fold the **31 orphan speakers** cleanup in here, or handle separately?
5. Should "merge" be undoable beyond the soft-deleted loser (e.g. keep a merge
   log to fully reverse a re-point)?

## A possible phasing (if we proceed)
- **6a (easy, high-ish value):** edit series/topic summaries + speaker/topic
  rename. Small, ships fast, immediately useful for the course pages.
- **6b (the careful one):** the duplicate-candidates table + side-by-side compare
  + merge (soft-delete loser). Fuzzy + shared-context signals only.
- **6c (optional, later):** AI/web-assisted ranking + speaker bio/photo
  enrichment — likely better as part of Direction D than bolted on here.

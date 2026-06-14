# Clayton TV — Where Next? Strategic Directions

*A discussion document for Ettie (and the team). Drafted 2026-06-14.*
*Plain-English up top; engineering + market detail in the appendices.*

---

## The moment we're in

Two things are true at once:

1. **The new platform is here and strong.** beta.claytontv.co.uk is a complete,
   redesigned library — a curated, calm, "media you can trust" experience with
   ~13,000 talks, course-style series pages, audience pathways, a watch
   experience with a persistent player, and (as of this week) **fast, typo-
   tolerant search** across the whole catalogue.

2. **The clock is ticking on how content gets in.** Today the library is fed
   automatically from the *old* clayton.tv site. **That old site is being
   retired in a few months — and when it goes, the automatic feed stops.**
   After that, every new talk has to enter through *this* platform.

So the central question isn't "is the site good?" (it is) — it's **"what should
Clayton TV become, and how does content flow into it once we're on our own?"**

That decision is also a doorway: there's real scope here to build not just a
replacement, but *a genuinely excellent Christian content platform* — one that
could, in time, be shared with other churches.

---

## One picture: the four layers

Think of the future as four layers that **stack** — each adds to the one below,
and each is a real, proven model used by platforms like it:

```
        ┌─────────────────────────────────────────────┐
   4    │  WHITELABEL  — other churches get their own    │   biggest
        │  branded space on the platform                 │   ambition
        ├─────────────────────────────────────────────┤
   3    │  CONTRIBUTORS — churches/people submit their    │
        │  own talks; Clayton TV approves before publish  │
        ├─────────────────────────────────────────────┤
   2    │  AUTOMATED INTAKE — talks flow in from YouTube/  │
        │  RSS + AI does the tagging; people just review  │
        ├─────────────────────────────────────────────┤
   1    │  CURATED LIBRARY — the trusted core (what we     │   essential,
        │  have today), managed by the Clayton TV team    │   urgent
        └─────────────────────────────────────────────┘
```

You don't have to choose one *forever* — you choose **how far up to go, and in
what order.** The directions below are really "how far up the stack, and with
what emphasis."

A thread that runs through all of it: **trust is the product.** The thing that
makes Clayton TV different from "just search YouTube" is that someone has
*curated* it. Every option below is designed to grow the library **without
giving that away** — which, in practice, means contribution can be open but
*publishing stays gated* by the Clayton TV team.

---

## The directions

### Direction A — "The Trusted Library" (do the core brilliantly)

**In a sentence:** Stay a single, centrally-curated Clayton TV library — and
replace the dying legacy feed with a modern, mostly-automated intake that the
team lightly oversees.

**What it feels like:** Exactly today's experience, but self-sufficient. New
talks appear automatically from a hand-picked list of trusted churches/ministry
YouTube channels and sermon feeds; the team reviews and tidies rather than types
everything from scratch.

**What it takes:** Automated intake (Layer 2) + a polished editorial workflow
for Ettie's team. No public logins. *Smallest, fastest, lowest-risk.*

**Trust & risk:** Highest trust (everything still passes the team's eye); the
main risk is simply *team time* to review.

**Why it matters:** This is the **floor** — the legacy retirement forces *at
least* this. Closest real-world model: **RightNow Media** and **Laracasts** —
their curated filter *is* the product.

---

### Direction B — "The Contributor Network" (let churches submit, we curate)

**In a sentence:** Give churches and trusted contributors their own login to
*submit* talks and fill in the details — but Clayton TV still approves
everything before it goes live.

**What it feels like:** A church secretary logs in, pastes a YouTube link, the
system auto-fills most of the details, they confirm the speaker/series, and it
lands in a **review queue**. Clayton TV clicks "approve" and it's published. The
heavy lifting is shared with the people who know the content best; the trust
gate stays with us.

**What it takes:** Everything in A, plus real **accounts & roles** and a
**moderation queue**. Medium effort.

**Trust & risk:** Trust preserved *because publishing stays central* — this is
the well-trodden "submit, don't self-publish" model (how **Ghost** handles
contributors). The risk is adoption (getting churches to bother) more than tech.

**Why it matters:** It's how the library grows beyond what a small central team
can personally enter — without becoming an un-curated free-for-all like open
YouTube.

---

### Direction C — "The Whitelabel Platform" (each church its own space)

**In a sentence:** Turn Clayton TV into a platform that hosts *many* churches —
each with its own branded area — while optionally feeding the best content into
a shared, trusted, cross-church library.

**What it feels like:** `st-marys.claytontv.co.uk` is St Mary's own tidy media
site (their logo, their colours, their sermons), run by them — and Clayton TV
curates a "best of" library across all of them. One platform, many front doors.

**What it takes:** Everything in A and B, plus a significant re-architecture so
the data is "per-church", plus church onboarding, branding controls, and more
operational overhead. *The biggest build — honestly 2–3+ weeks of focused
foundation work before features, and ongoing ops.*

**Trust & risk:** Powerful and on-mission (serve the wider church), but the
classic traps are real: **custom domains and per-church databases multiply
ongoing maintenance** — start with simple subdomains and one shared database.
And **multi-brand theming fights the elderly-friendly consistency** we've worked
for — so any per-church styling must stay inside safe, accessible guardrails
(logo + one accent colour, not free-form design). Closest model: **Subsplash**
(one platform, each church a branded tenant).

**Why it matters:** This is the long-term "amazing platform shared with other
churches" vision — best treated as a *destination to design toward*, reached
**after** the single-church version is rock-solid.

---

### Direction D — "The AI Content Engine" (the differentiator, layered on any of the above)

**In a sentence:** Make the library do things a plain video list can't —
search *inside* sermons, auto-tag topics, auto-link Bible passages, auto-create
shareable clips — by transcribing everything and letting AI assist.

**What it feels like:** "Find the talk where he explains grace through the
prodigal son" actually works. Every talk auto-knows which Bible passages it
covers (browse-by-book becomes effortless). Short clips for social media
generate themselves. The team *reviews AI suggestions* rather than typing
metadata.

**What it takes:** This isn't a separate destination — it's a **capability that
supercharges A, B, or C.** The keystone is cheap **auto-transcription** (the
whole catalogue for roughly the price of a few meals out); once we have
transcripts, the rest is inexpensive AI with a human approving the results.

**Trust & risk:** Low if we keep "**AI proposes, human disposes**" — every
auto-generated tag/summary is a suggestion someone accepts. (One note for later:
if we publish AI-edited *clips*, new EU labelling rules from Aug 2026 may apply.)

**Why it matters:** This is what turns "a tidy video archive" into "a Christian
content platform people talk about." It's mostly **easy/medium** wins for a
small team, and it makes every other direction better.

---

## Recommendation: a phased path, not a single bet

The four layers are additive and each has a proven template, so the sensible
play is a **sequence**, with the AI engine woven in from the start:

1. **Now (forced by the clock): Direction A + start of D.**
   Build the automated intake that replaces the legacy feed, and turn on
   auto-transcription + AI-assisted tagging so the team *reviews* rather than
   *types*. This keeps the library alive and immediately better.

2. **Next: Direction B.**
   Add contributor accounts + a review queue so churches share the load — trust
   intact because we still approve. (This also needs the real login system that
   Epic 3 / "auth & editorial admin" was already pointing at.)

3. **Later, deliberately: Direction C.**
   Once single-Clayton-TV is humming, design the whitelabel/multi-church layer —
   starting with simple subdomains, one shared database, and guard-railed
   branding. Treat it as the north star to design toward, not the next sprint.

**The one urgent thing to decide soon:** how content gets in once the legacy
site dies. Everything else can follow; that one is on a timer.

---

## Questions for Ettie

These are the choices only she/the team can make — worth bringing to the
conversation:

1. **How "hands-on" should curation be?** Review *everything* (max trust, more
   time), or auto-publish from a trusted-source list and spot-check (less time,
   slightly more risk)?
2. **Do we want other churches contributing** (Direction B) — and if so, who's
   the first friendly church to pilot with?
3. **Is the multi-church/whitelabel vision (C) a "yes, eventually"** we should
   design toward now, or a "maybe one day" we keep out of scope?
4. **Which AI features excite her most?** (transcript search · auto Bible-passage
   linking · auto-summaries · social clips) — to prioritise within D.
5. **What does "trust" mean editorially?** What would make a talk *not* belong in
   Clayton TV? (This defines the review/moderation bar.)

---

## Appendix 1 — Engineering reality (for Jamie)

- **Single-tenant today.** No `church_id` on any model; one database; URLs
  hardcoded to claytontv.co.uk. The relational model is *clean* and would extend
  to multi-tenancy without contortions, but the tooling (per-church permissions,
  per-church search scoping, onboarding, branding, deploy/observability) is a
  real ~2–3 week foundation before any tenant features. → **C is genuinely big;
  A and B are not.**
- **Auth is a stub.** The Inertia shared user is a hardcoded "Test User"; no
  route protection or roles exist yet. B and C both depend on building this
  first (the existing "Epic 3 — auth & editorial admin"). The Django `/admin`
  (now branded + all models registered) works today for the central team.
- **Content already auto-indexes.** Save a video → it's searchable in seconds
  (Typesense signals) → so new intake paths "just work" for search.
- **The legacy-death gap is the forcing function.** When clayton.tv retires, the
  hourly sync stops; without an intake replacement, the catalogue freezes. This
  is the only item on a hard timer.
- **Watch the existing traps:** strict Inertia encoder (no raw models as props),
  the decoy relations (`Video.series` FK / `Video.ministry` M2M unpopulated —
  count `Series.videos`), destructive legacy importers (don't reuse), SQLite-
  local vs Postgres-beta differences.

## Appendix 2 — How comparable platforms are built

- **Curated libraries (our core):** RightNow Media, Laracasts — central editorial
  curation *is* the trust. Churches can't self-publish into the main catalogue.
- **Contributor model (B):** Ghost CMS — "Contributor" role writes/submits but
  **cannot publish**; central team publishes. Pair with Patreon-style *graduated*
  moderation (hide one item, human review) rather than all-or-nothing.
- **Whitelabel (C):** Subsplash — one platform, each church a branded tenant.
  Architecture: **subdomains + one shared database with a tenant column** is the
  flat-ops default; **custom domains + per-tenant databases are the small-team
  trap** (perpetual SSL renewals, migrations multiplied per church). Constrain
  theming for accessibility.
- **Don't** try to out-build Subsplash/Tithe.ly as an all-in-one church tool
  (giving, ChMS, websites) — that market is crowded and well-funded. Clayton
  TV's edge is the *curated library*.

## Appendix 3 — Content intake options (replacing the legacy feed)

| Option | Automation | Metadata quality | Effort | Best for |
|---|---|---|---|---|
| **YouTube channel/playlist polling** | High | Medium (titles/dates/durations free; *not* speaker/series/topic) | Medium | Bulk from trusted ministry channels |
| **Sermon RSS / Podcasting 2.0 feeds** | High | Medium–High (often carries speaker, series, Bible ref; sometimes free transcripts) | Medium | Churches with structured feeds |
| **Church self-submission portal** | Low–Med | Highest (the source knows the truth) | Med–High | The durable long-term front door (Direction B) |
| **Manual editorial entry** | None | Highest, slowest | Low (admin exists) | Flagship content + safety net |
| **Hybrid (recommended)** | High where it counts | High after AI + review | Med–High | The realistic operating model |

*Quota note: poll known playlists (~1 unit each), avoid YouTube `search.list`
(100 units). Transcripts: generate with Whisper (~$0.30/hour) rather than
scraping — official captions only work on videos you own.*

## Appendix 4 — Automation building blocks (Direction D)

Priority order for a small team (transcription is the keystone that unlocks the
rest):

1. **Auto-transcription** (Whisper/Deepgram) — *easy*, ~$0.18–0.36/hour. Foundation.
2. **AI tagging: topics, audience, summaries** — *easy*, pennies/video.
3. **Bible-passage detection & linking** — *easy*, free libraries exist.
4. **Transcript / semantic search** — *easy–medium* (Typesense already in place).
5. **AI-suggested series grouping & speaker ID** — *medium*.
6. **Auto chapter markers** — *medium*.
7. **Trust/moderation signals** (auto-flag for human review) — *medium*.
8. **"Best clip" extraction for social** — *medium–hard*.

*Principle throughout: AI proposes, a human approves. Curate the source, then
sample the item.*

---

*Sources for the market & automation research are recorded in the session notes;
key references include RightNow Media, Subsplash, SermonAudio, Ghost, Laracasts,
the YouTube Data API & Podcasting 2.0 specs, and current Whisper/LLM pricing.*

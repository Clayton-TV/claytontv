# Clayton TV Revamp — Master Plan

> Living document. Owner: Jamie Gardner (@thatgardnerone). Started 2026-06-12.
> Sign-off authority for the beta release: Ettie (project director) + Frances (data lead).

## 0. Current status — update every session

**As of 2026-06-12 (evening):**
- ✅ Epic 0 complete (toolchain, Inertia v3 spike, test harness, CLAUDE.md).
- ✅ Epic 1 complete: beta live at https://beta.claytontv.co.uk (full
  catalogue), push-to-deploy from `beta`, server hardened/upgraded
  (docs/DEPLOYMENT.md). Observability wired (#175): Sentry + cookieless
  PostHog + CONN_HEALTH_CHECKS — **activation awaits two values from Jamie:**
  `SENTRY_DSN` in the beta `.env` and `VITE_POSTHOG_KEY` as a GitHub beta
  environment secret.
- ✅ Epic 2.0 rescue resolved: no legacy transcript corpus ever existed (links
  were external references); bit.ly rot defused; legacy admin ID→name lookup
  tables captured (data/legacy_rescue/lookups/). Live admin's newest programme
  is ID 12404 vs the dump's 10732 — **~1,670 programmes added since the dump**,
  raising the priority of Epic 2's incremental sync.
- ✅ Livestreams live on beta: 654 flagged via backfill_livestream_flags
  (importer had the column commented out); homepage "Watch Live" hero now
  shows. Run the backfill after deploys until the importer rework lands.
  "Live now" detection needs the YouTube Data API (keyless embed is dead,
  Error 153) → Epic 4.
- ✅ Series counts fixed (every series showed "0 programmes" — counted the
  never-populated FK instead of the Series.videos M2M).
- ✅ Epic 6 phase 1 polish deployed (#176): mobile horizontal overflow fixed
  (w-svw overlay), keyboard-focusable cards, visible active-nav, lazy images,
  reduced-motion-safe micro-interactions, 44px targets, brand tokens.
- ✅ Epic 6 phases 6.0–6.3 deployed (#177): redesign direction approved via
  mockup, typography roles (Lexend/Inria), new app shell (reka-ui Sheet nav —
  Headless UI gone, SSR mismatch source removed), curated homepage (props
  299 KB → 6.1 KB). Vue Motion deferred to 6.7 by design decision.
- ✅ Epic 6.4 + cohesion slice deployed (#178): watch page redesigned with a
  deferred "More in this series" rail (first Inertia v3 deferred prop),
  Browse/Search restyled to the language, hover prefetch across nav/cards/
  chips.
- ✅ Epic 6.5 deployed (#179): /series course landing + /series/<name> course
  pages + /topic grouped chips. Fixed the series zero-episode bug (third face
  of the decoy-relation trap) and the browse_categories N+1 sweep.
- ✅ Epic 6.5b deployed (#180): Speakers/Books/Ministries directories, IA
  consolidation (demographics → Topics audiences; /catalogue deleted; channels
  demoted), homepage below-fold sections scroll-deferred via optional() +
  WhenVisible. Every public page now speaks the design language.
- ✅ Epic 2.1 deployed + run on beta postgres (#181): in-repo idempotent
  ingestion (catalogue/ingest), upserts keyed on legacy IDs, run-twice no-op
  proven at full 9,496-programme scale. Recovered: 1,782 related-resource
  links (949 transcripts), 74 multi-host URL sets, normalized labels by ID.
  227 duplicate listings itemized. Supersedes the ctvDBreform CSV path for
  programmes; series.json hierarchy is 2.2's job.
- ✅ Epic 2.2 live on beta: series hierarchy ingested (2,287 nodes, 15,027
  ordered memberships, number_in_series, clean names — 690 mangled ones
  fixed), livestream flags now owned by the authoritative LIVE STREAMS tree,
  series URLs by stable id_number.
- ✅ Epic 2.3 deployed: in-repo live-admin sync (same upsert core, cookie
  auth with expiry detection, hourly cron installed on beta). **Activation
  awaits Jamie pasting a fresh LEGACY_ADMIN_COOKIE into the beta .env**
  (runbook in docs/DEPLOYMENT.md) — then the ~1,670 missing programmes
  backfill via `sync_live_admin --pages 40` once, and hourly sync after.
  ClayScraper + ctvDBreform are now fully superseded.
- ✅ Epic 6.6 deployed (#182): destination pages — speaker detail (avatar,
  talk count, deferred "featured in these series", talks) and series detail v2
  (numbered episode rows from number_in_series, "Start from the beginning").
  Confirmed speaker bio/photo fill-rate is zero.
- ✅ Epic 6.6b deployed (#183): Bible book pages with passage navigation —
  title-parsed chapter strip, ?chapter= filter, reference badges. Pure
  derivation (catalogue/passages.py), no schema change. The spec's novel one.
- ✅ Watch page enriched (#184): passage badge (links to the chapter) +
  rescued transcript/audio companion links. Book chapter strip now an
  auto-fill grid that fills the row edge-to-edge.
- ✅ Epic 6.6c deployed (#185): speakers index pivoted to lookup-first +
  featured voices + scroll-deferred A–Z directory. **The destinations round
  is complete** — every page from the design spec's first wave now ships its
  intended answer.
- ✅ Quick wins deployed (#187): share button (native sheet + copy/WhatsApp)
  and localStorage watched-memory (ticks on cards + episode rows), no accounts.
- ✅ 6.9 slice 1 deployed (#188): Latest is a time-grouped feed with
  series-flood collapse and a new-since-last-visit divider.
- ✅ 6.9 slice 2 (#189): the player API layer — usePlayer over the YouTube
  iframe API + Vimeo SDK; true resume ("Resuming from 14:32 · Start over"),
  watched-at-80% (replaces watched-on-open), autoplay-next through a series,
  playback keys (space/k, ←/→, m). Verified end-to-end in Claude Preview:
  a 42s episode played out, ended, navigated, and the next episode autoplayed.
  NOTE: Claude-in-Chrome cannot stream media (player UIs load, media stalls) —
  use Claude Preview for playback verification.
  ▶️ **Next in 6.9: command palette (⌘K, shadcn Command) + global shortcuts →
  persistent mini-player → continue-watching rail; transcript embeddings as a
  parallel backend track (folds into Epic 5). Then 6.7 motion pass and 6.8
  light mode + empty states + WCAG audit close Epic 6. Epic 2
  leftovers: ministry trees, series covers (first-episode thumbnail), the
  227 duplicate-URL programmes from 2.1. (✅ Series dedup done: 2,667→1,905,
  orphans + identical browse-tree twins collapsed in the ingestion.)
  Epic 4 (YouTube API) awaits Workspace creds; sync activation awaits
  LEGACY_ADMIN credentials in the beta .env.**
- Waiting on: Vimeo account answers from Ettie (asked 8pm 2026-06-12);
  Google Workspace creds when Epic 4 starts.
- Dependabot triage: npm transitives fixed on beta (#174); remaining alerts
  mostly affect main's stale lockfiles.

## 1. Mission & urgency

Clayton TV provides Christian media you can trust. The legacy site (`clayton.tv`) is
expected to die within weeks–months and there is no funded mitigation — this revamp
*is* the mitigation strategy. We build on the long-lived `beta` branch, deploy to
`https://beta.claytontv.co.uk`, and invite Matt and Jonathan to swap onto this trunk
once it is stable. Their in-flight work on `main` stays untouched.

**Primary jobs to be done:**
- A congregant (often elderly, on a phone) watches Sunday's service with zero friction.
- A minister or student finds every talk on a passage/topic/speaker — including inside
  transcripts.
- Ettie (or a delegate) adds and curates content through one trusted admin account.

## 2. Working agreement

- **Branching:** `beta` is the trunk for this revamp. Feature branches off `beta`,
  merged via PR when CI is green. `main` belongs to the existing live-site work.
- **Cadence:** Epic → focused session subplans → TDD loop. An Epic is *done* when:
  deployed to beta, integration-tested in a real browser (Claude in Chrome),
  core-flow screenshots reviewed, and a written retrospective folded into the next Epic.
- **Testing:** TDD with meaningful, feature-level coverage. **Never trust the legacy
  data** — column names and content are quirky; every import/transform behaviour is
  verified against real sample data, not assumptions.
- **Style:** Clean code, minimal abstraction. Thin views → plain service functions →
  models. Boring technology. A junior dev or an AI agent should be able to pick up any
  module cold.
- **Safety:** Database backup before every migrate in every deploy. (Lesson of #92.)

## 3. Architecture principles

1. Monolith-first Django; no API layer beyond Inertia props until a real need exists.
2. Idempotent data pipelines: upsert on stable natural keys (legacy ProgrammeID / ref),
   dry-run mode, never `delete()`-then-reload.
3. Background jobs are plain Django management commands scheduled by cron/supervisord —
   no Celery cluster.
4. Progressive disclosure UX: the elderly-first surface stays simple; power features
   (advanced search, keyboard nav) live one layer down.
5. Observability from day one: Sentry (errors) and PostHog (privacy-respecting product
   analytics) on Jamie's existing infra — `sentry.tgo.dev` / `posthog.tgo.dev`.
6. Design engineering per Emil Kowalski / animations.dev: animation communicates state,
   <300 ms, ease-out entrances, `prefers-reduced-motion` respected, zero layout shift,
   44 px touch targets, WCAG 2.1 AA.

## 4. Epics

### Epic 0 — Foundations & toolchain *(in progress)*
Goal: modern toolchain + a safety net, before any feature work.
- ✅ **0.1 Toolchain migration:** Poetry → uv; Python 3.12 → 3.14; Django 5.2 → 6.0;
  psycopg2 → psycopg 3; poe tasks and README updated; CI on uv.
- ✅ **0.2 Inertia v3 / SSR spike:** adopted v3 via adapter-template override;
  SSR opt-in pending the nav rework — see decision log.
- ✅ **0.3 Test harness** (PR #173): factory-boy factories, Inertia test helper,
  feature tests for homepage/watch/search, query-count regression test, 60%
  coverage gate in CI (65% at introduction — ratchet upward). Killed the
  homepage N+1 that 504'd beta.
- ✅ **0.4 Agent/team docs:** CLAUDE.md (commands, workflow, architecture traps),
  README quickstart for the uv world, Herd proxy local HTTPS.
- Exit: CI green on `beta`, dev server runs on 3.14/Django 6 locally, decision log
  updated.

### Epic 1 — Beta environment & observability
Goal: a deployable, observable beta target. (Needs SSH access + Cloudflare subdomain.)
- nginx vhost + certbot for `beta.claytontv.co.uk`; `gunicorn-claytontv-beta` systemd
  service; separate beta database; shared `.env`/media dirs.
- `deploy-to-beta.yaml` workflow triggered from `beta` branch, with **pre-migrate DB
  backup** step.
- Sentry SDK (DSN → sentry.tgo.dev) and PostHog (→ posthog.tgo.dev) wired in,
  gated behind cookie consent.
- Exit: smoke page live on beta with an intentional test error visible in Sentry and a
  pageview in PostHog.

### Epic 2 — Data rescue & idempotent pipeline
Goal: get all recoverable legacy data safe, and make imports non-destructive.
- ✅ **2.0 Emergency rescue — resolved; scope was misdiagnosed.** The dump's
  transcript/audio "links" were always external reference links
  (printandaudio.org.uk, desiringgod.org, paultripp.com), never hosted files —
  see data/legacy_rescue/README.md. The one genuine rot risk (162 bit.ly links)
  is defused: resolved to permanent URLs in
  data/legacy_rescue/external_resource_links.csv. Nothing else of value lives on
  the dying server (its 13 self-hosted thumbnails were already 404; #81
  fallbacks cover those videos). **Transcript search will be built on YouTube
  captions (Epic 4), not a legacy corpus.**
- Extend the Video model: related external resources (from the rescue mapping),
  multiple platform URLs (the dump holds ~9.6k YouTube and ~9.6k Vimeo URLs;
  today only `media[0]` survives).
- Replace delete-all importers with upserts keyed on legacy ProgrammeID/ref; restore
  the unique constraints dropped "for testing" (#86); fix series→video linking; handle
  the 37 duplicate legacy refs and comma-in-topic names (#88) explicitly.
- Unify ctvDBreform's `scraperimport` schema with the `legacyimport` format so scraped
  rows can actually import.
- Feature-level tests against real quirky CSV samples for every behaviour above.
- Exit: a full re-import on beta is idempotent (run twice → identical DB), with
  transcripts present and counts reconciled against the legacy dump.

### Epic 3 — Auth & editorial admin
Goal: real authentication and a workable editorial flow for Ettie/delegates.
- Remove the hardcoded fake "Test User" from Inertia shared props.
- One admin account (Ettie or delegates); Django admin polish for the add/curate flow;
  document the workflow for volunteers.
- Sanitize HTML descriptions (#110 — XSS-shaped) on render and/or batch-clean.
- No public sign-in (out of scope unless trivially cheap later).

### Epic 4 — YouTube livestream MVP (the headline feature)
Goal: Sunday livestream → searchable library, automatically.

**Product spec (Jamie, 2026-06-12):** "Given I'm an older church member who
can't attend the morning service today, when I go to claytontv near the
livestream's start time, then I see an option to play the livestream when it
starts." Live/upcoming is ephemeral, API-driven state; once a stream ends it
archives into the main library for search/reference. Model *provenance*
(`is_livestream` — it was streamed) separately from *broadcast state*
(upcoming/live/ended + scheduled start, from the API). Open product questions
for Ettie: how early to surface the upcoming stream (15 min? 1 h? persistent
"next service" slot with countdown — recommended for elderly early-arrivers);
whether archived streams merge into "Latest" or sit behind a "Services"
filter (weekly services would otherwise flood it).
- YouTube Data API client (creds from Jamie's Google Workspace; channel
  `UCvME6kEF02MqliB5TNHFLZA`; spike notes in #109).
- Scheduled jobs (cron/supervisord): discover upcoming/live broadcasts; livestream page
  auto-switches to the upcoming stream ~1 h before start (#6); after the stream ends,
  transition the VOD into the catalogue and fetch its transcript/captions.
- Failure alerting (Sentry + email to the editorial account, per #12's intent).
- Exit: a real Sunday stream observed end-to-end on beta: live page → library entry
  with transcript, untouched by human hands.

### Epic 5 — Search (Typesense + transcripts)
Goal: instant, typo-tolerant search across titles, taxonomy, and transcript text.
Builds on Matt's stalled Typesense exploration (#167) — we own it now, on our branches.
- Typesense provisioned on the server (the open infra question from #167).
- Index videos/series/speakers/topics + transcript text; reindex hooks on import and
  on livestream transition.
- Instant-search UI; advanced filters (bible book, speaker, topic — #7).
- Exit: search "Romans 8" and find talks whose *transcript* mentions it.

### Epic 6 — full redesign (supersedes the #164 "polish the existing layout" framing)
Goal: redesign the entire site from use cases — not iterate the inherited
layout. Reference model: **Laracasts, not YouTube** — an editorial content
library (curation, calm, series-as-courses, one clear next action per screen),
matching the "media you can trust" brand and the elderly-first/power-depth
philosophy. Built on shadcn-vue (reka-ui) components, atomic design structure,
CSS transitions + Vue Motion (@vueuse/motion). Long-term vision to design for
(not build yet): a multi-church community platform with courses, notes and
materials.

- ✅ **6.0-pre (done as old phase 1):** interaction hygiene — focus rings,
  reduced motion, tap targets, mobile overflow fix, lazy images. Carries over.
- **6.0 Design direction:** IA + page blueprints (home, watch, series, topic,
  browse, search), type scale (Inria Sans display / Lexend body), spacing
  system, component inventory. Mockups reviewed with Jamie (+ Ettie) BEFORE
  rebuild. Personas drive every screen: elderly member ("watch this Sunday's
  service in two taps"), student/minister ("find every talk on Romans 8").
- **6.1 Design-system foundation:** finish tokens (incl. light mode values),
  typography plumbing, install @vueuse/motion, adopt the shadcn component set
  (Button, Card, Badge, Input, Sheet, Tabs, Skeleton, DropdownMenu, Dialog),
  atomic directory structure.
- **6.2 App shell:** header/nav rebuild on reka-ui (SSR-safe — unblocks
  default-on SSR), mobile Sheet menu, footer, search affordance.
- **6.3 Homepage:** purpose-led hero + "next service" slot (pairs with Epic 4),
  curated rails (latest, featured series, topics) — replaces the 1,069-card
  dump and its 296 KB payload.
- **6.4 Watch page:** player + structured metadata, series "up next" rail,
  related content.
- **6.5 Series & topic pages:** the Laracasts course-page pattern — cover,
  summary, ordered episode list; topic landing pages.
- **6.6 Browse + search experience:** filters, instant search UI (fronts the
  Typesense work in Epic 5).
- **6.9 Connected app layer** (added 2026-06-12; spec: DESIGN_SPEC.md §
  "Connected app layer"): the shift from pages-that-show-lists to an app with
  a player at its heart. (a) Latest feed regroup — time groups, series-flood
  collapse, new-since-last-visit divider, facet chips; (b) `usePlayer`
  postMessage layer over the YouTube iframe API + Vimeo SDK → true resume,
  watched-at-80%, autoplay-next, continue-watching rail; (c) ⌘K command
  palette (shadcn Command) + global shortcuts; (d) persistent mini-player in
  AppLayout (fixed-position iframe over a watch-page placeholder — never
  remounts). Power depth stays invisible until invoked. Transcript
  embeddings (pgvector semantic search) folds into Epic 5.
- **6.7 Motion pass:** Vue Motion entrances/staggers where they communicate
  (page-level), CSS for micro-state. <300ms, reduced-motion always.
- **6.8 Light mode, empty states, image perf, WCAG AA audit** (axe-core +
  Lighthouse), screenshot review with Ettie.
- Exit: every #164 sub-issue closed or superseded; Lighthouse a11y/perf pass;
  sign-off review.

### Epic 7 — Hardening & cutover readiness
Goal: beta is the credible successor.
- Redis caching for hot pages; query audit; SSR finalized (v3 adapter status permitting).
- Full integration sweep of core flows via Claude in Chrome; perf budget check.
- Cutover plan: DNS swap runbook, redirects from legacy URLs (`programmeRef` mapping),
  volunteer/admin documentation, Ettie + Frances sign-off checklist.

## 5. MoSCoW (settled 2026-06-12)

**Must:** Epics 0–5 inclusive — toolchain, beta env + Sentry/PostHog wiring,
idempotent imports + related-resource metadata (rescue artifacts in
data/legacy_rescue/), real auth (single admin), YouTube livestream MVP with
caption/transcript fetch, transcript-aware Typesense search, a11y/UX baseline
(light mode fix, sanitized descriptions, WCAG AA basics).

**Should:** Inertia v3 + SSR (gated on adapter spike), full #164 revamp polish,
automated ingest from trusted channels (#12), advanced search filters (#7), scraper
hardening (only while the legacy site survives and double-entry continues), mobile nav
overhaul.

**Could:** report-a-problem (#83), per-church livestream links + simultaneous-stream
carousel (#6/Keswick), user display preferences (#23), audio-only mode (#69), public
user accounts (only if trivial), PostHog-driven iteration dashboards, volunteer import
training docs (#96).

**Won't (this phase):** church self-streaming (#85), kid-safe mode (#11), seeker
journeys (#21), staff page (#28), native apps, replacing Vimeo hosting, rewriting
Matt/Jonathan's in-flight main-branch work.

## 6. Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Legacy site dies before data rescue | Permanent content loss (esp. transcripts/audio) | Epic 2.0 emergency mirror runs ASAP, independent of other work |
| inertia-django lags Inertia v3 (#99) | Blocks v3 features/SSR-DX | Spike in 0.2; fallback = v2 client + adapter SSR; consider upstream PR |
| Destructive importer pattern recurs | DB wipe (happened: #92) | Upserts only; pre-migrate backups; idempotency test in CI |
| Single server hosts prod + beta | Resource contention, blast radius | Separate DBs/services; observability; Jamie owns the box |
| Legacy data quirks | Silent corruption | No assumptions; feature tests on real samples; reconciliation counts |
| Solo-owner bus factor | Project stalls | This doc + CLAUDE.md + ADRs keep context transferable to any dev/agent |

## 7. Decision log (ADR-lite)

- **2026-06-12 — Governance:** Jamie takes sole ownership on `beta` branch → beta env;
  main untouched; Ettie+Frances sign off the beta release.
- **2026-06-12 — Observability:** reuse Jamie's existing self-hosted
  sentry.tgo.dev + posthog.tgo.dev rather than standing up new instances.
- **2026-06-12 — Auth scope:** single shared admin account; no public sign-in.
- **2026-06-12 — Search:** continue Typesense direction from #167 under our ownership.
- **2026-06-12 — Inertia v3 (spike 0.2 outcome):** adopted `@inertiajs/vue3` 3.4 against
  inertia-django 1.2 via a project-level `templates/inertia.html` override that emits the
  v3 JSON-script-tag protocol (plus the `inertia_page_json` template filter for safe
  embedding). Verified in-browser: client boot, SPA navigation, SSR render + hydration.
  SSR is **opt-in** (`INERTIA_SSR_ENABLED` env, `npm run build-ssr && npm run ssr`) and
  stays off by default until the Headless UI v1 nav in AppLayout — the one component
  with SSR hydration mismatches — is replaced by the reka-ui nav (Epic 6, #154).
  Remove the override when upstream lands v3 support (inertia-django#99). Avoid v3
  features needing new server support (`useHttp`, once props, infinite scroll) until then.
- *(pending)* — Vimeo account future (Ettie).
- *(pending)* — 2 AM pipeline contents (observe legacy behaviour).

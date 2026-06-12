# Clayton TV Revamp — Master Plan

> Living document. Owner: Jamie Gardner (@thatgardnerone). Started 2026-06-12.
> Sign-off authority for the beta release: Ettie (project director) + Frances (data lead).

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
- **0.4 Agent/team docs:** CLAUDE.md, contributor quickstart for the uv world,
  Herd proxy local HTTPS (`herd proxy claytontv http://127.0.0.1:8000 --secure`).
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

### Epic 2 — Data rescue & idempotent pipeline ⚠️ time-critical
Goal: get *all* recoverable legacy data safe before clayton.tv dies, and make imports
non-destructive.
- **2.0 Emergency mirror (can run before/parallel to anything):** download the 953
  transcript files + 836 audio links referenced in the legacy dump; archive raw dumps
  and scraped CSVs off-site.
- Extend the Video model: transcript (text + source), audio link, multiple platform
  URLs (the dump holds ~9.6k YouTube and ~9.6k Vimeo URLs; today only `media[0]`
  survives).
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

### Epic 6 — UI/UX revamp (adopts tracking issue #164)
Goal: the design-engineering pass — mobile-first, elderly-first, delightful.
- Phased per #164: design tokens (#150, incl. fixing the hardcoded dark mode),
  typography (#151), shadcn theme to Clayton aesthetic, micro-animations with CSS +
  Vue Motion (#152), video card (#153), nav (#154), homepage (#155), watch page (#156),
  category/pagination (#157), footer (#159), toasts (#160), image perf (#161), mobile
  overhaul (#162), empty states (#163), WCAG AA audit (#158).
- Exit: axe-core/Lighthouse pass, reduced-motion honoured, screenshot review with Ettie.

### Epic 7 — Hardening & cutover readiness
Goal: beta is the credible successor.
- Redis caching for hot pages; query audit; SSR finalized (v3 adapter status permitting).
- Full integration sweep of core flows via Claude in Chrome; perf budget check.
- Cutover plan: DNS swap runbook, redirects from legacy URLs (`programmeRef` mapping),
  volunteer/admin documentation, Ettie + Frances sign-off checklist.

## 5. MoSCoW (settled 2026-06-12)

**Must:** Epics 0–5 inclusive — toolchain, beta env + Sentry/PostHog wiring, data
rescue + idempotent imports + transcript capture, real auth (single admin), YouTube
livestream MVP with transcript fetch, transcript-aware Typesense search, a11y/UX
baseline (light mode fix, sanitized descriptions, WCAG AA basics).

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

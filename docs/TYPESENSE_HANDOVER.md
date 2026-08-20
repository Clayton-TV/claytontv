# Typesense Hybrid Search — Handover

> **Historical brief — the search epic (#213) has shipped.** This is the
> original kickoff document, kept for background and rationale. Its environment
> notes predate the three-tier `dev` → `beta` → `main` restructure (in
> particular "prod/`main` belongs to the legacy team — do not touch" and
> "deploy = push to `beta`" are no longer the whole picture). For current
> environments, per-env Typesense instances and the deploy flow, read
> [DEPLOYMENT.md](DEPLOYMENT.md) — it wins where the two disagree.

**Kick this off in a fresh session.** Self-contained brief for adding Typesense
as the search backend behind the existing instant client tier. Tracking issue:
[#213](https://github.com/Clayton-TV/claytontv/issues/213).

---

## Goal
Replace the `icontains` search tier with **Typesense** for typo-tolerance,
relevance ranking, server-side **synonyms**, and fast faceting — **keeping the
instant client-side tier** we already have. Net UX: results feel instant, then a
beat later the authoritative, ranked, typo-tolerant matches stream in.

## Current state (June 2026, post-overhaul)
- **Search today = ORM `icontains`** in three places in `app/views.py`:
  - `palette(request)` → `/api/palette` (the ⌘K palette; JSON; debounced per keystroke)
  - `search(request)` → `/search` page (Inertia)
  - `browse_faceted` / `app/browse.py` → `/browse` facet counts
- **Palette is already two-tier**: reka-ui `useFilter` filters the in-memory
  static commands instantly (`Command.vue`/`CommandItem.vue` — supports a
  `keywords` prop), while `CommandPalette.vue` debounce-fetches `/api/palette`
  for catalogue hits. **Swapping the server tier to Typesense is a drop-in
  replacement of those view bodies** — the client tiers and JSON/Inertia
  response shapes don't change.
- **No Typesense, no Docker on app03 yet.**
- Supporting pieces already shipped: strict Inertia encoder (props must be
  dicts), flash/`Toaster` (can surface index errors), `video_card_props()` for
  card serialization.

## Server facts (for the infra phase)
- Host `app03.tgo.dev`, SSH port **2202**, user `jamie`, **passwordless sudo**.
  Standing **read-only** SSH auth is granted; **writes/installs need explicit
  confirmation** each time.
- Beta root `/srv/beta-claytontv`, prod `/srv/claytontv`. **Prod/`main` belongs
  to the legacy team — do not touch.** Do beta first; prod is a later,
  coordinated step.
- Deploy = GitHub Actions on push to `beta` (build → rsync to a release dir →
  `uv sync` → collectstatic → migrate → symlink swap → gunicorn restart). nginx
  vhosts in `/etc/nginx/sites-available/{beta-claytontv,claytontv}`; `/static/`
  is `alias …/current/staticfiles_collected/`. Env in
  `/srv/<env>/shared/.env`. Ubuntu 24.04.

## Approach (decided with Jamie)
Self-host a Typesense container on app03; Django proxies queries server-side
(API key never reaches the browser); **graceful ORM fallback** if Typesense is
unreachable so search never hard-fails.

---

## Phases (each its own branch/PR to `beta`)

### A — Infra: Typesense container on app03 (beta)
- SSH (with confirmation) → install Docker Engine + compose plugin (Ubuntu repo),
  enable the service.
- A **persistent** compose service (live under `/srv/beta-claytontv/shared/`, NOT
  the per-deploy release dir): `typesense/typesense:<pinned>`, **bind
  `127.0.0.1:8108` only**, named volume for `/data`, `--api-key` from an env
  secret, `restart: unless-stopped`, healthcheck on `/health`.
- ufw: **do not** open 8108 (loopback only — Django is the sole client).
- Document the container + ops (start/stop/reindex) in `docs/DEPLOYMENT.md`.

### B — Schema + client wrapper
- `pyproject` dep `typesense`; `catalogue/search.py` = a thin client built from
  settings (`TYPESENSE_HOST/PORT/API_KEY`).
- **Collection design** (decide in the spike): unified `content` collection with
  a `kind` field vs per-model collections. Index, per video: `name`,
  `description`, speaker/series/topic names, bible-book **display** names,
  `date_recorded` (int64, for sort), `duration_seconds`, `is_livestream`,
  demographic, `id`, `url`. Plus `series`/`speakers`/`topics`/`books`/
  `ministries` with their video counts (for ranking). Configure **synonyms** and
  a `default_sorting_field`.

### C — Indexing pipeline
- `manage.py reindex_search` — full rebuild (batched).
- Incremental upserts via `post_save` / `m2m_changed` signals on `Video` + its
  relations (start **synchronous**; move to a queue only if needed).
- Periodic **reconcile** cron to heal drift. **Reindex after the destructive
  importers** (they delete-all-then-reload).

### D — Django query proxy (behind ORM fallback)
- Rewrite the bodies of `palette` and `search` (and optionally `browse_faceted`
  facet counts) to query Typesense, returning the **same** JSON/Inertia shapes
  so the frontend is untouched.
- Wrap every Typesense call so an outage falls back to the current ORM query;
  report the failure to Sentry. API key stays server-side.

### E — Frontend polish (minimal)
- Palette: a subtle loading shimmer for the server tier while the instant client
  tier shows immediately.
- `/search` + `/browse` keep Inertia `defer`/`WhenVisible` for the heavy lists.

---

## Config / secrets
`TYPESENSE_API_KEY`, `TYPESENSE_HOST=127.0.0.1`, `TYPESENSE_PORT=8108` in
`/srv/beta-claytontv/shared/.env`. Local dev: optional docker-compose Typesense
so devs can run it; otherwise the ORM fallback keeps search working without it.

## Testing
- Unit: index-doc shape; proxy returns ranked results; **fallback path when
  Typesense is down** (mock the client).
- Feature: palette + `/search` return expected hits including a **typo** case and
  a **synonym** case.
- Perf sanity against the full imported catalogue (SQLite local vs PostgreSQL
  beta — see CLAUDE.md).

## Rollout
1. Spike schema + indexing locally (Typesense via local Docker) against the full
   catalogue.
2. Stand up the beta container; full `reindex_search`.
3. Ship the proxy **behind the ORM fallback**; verify on beta.
4. Wire signals for live upserts + the reconcile cron.

## Gotchas (codebase-specific)
- **Decoy relations:** `Video.series` FK is never populated — series membership
  is the `Series.videos` M2M (`Count("videos")`); `Video.ministry` M2M is
  unpopulated. Index from the **populated** relations or you'll index nothing.
- **Never pass models as Inertia props** (the strict encoder enforces this) —
  build dicts; reuse `app/cards.py::video_card_props`.
- **Destructive importers** — always reindex after a run.
- **Bible-book names** are choice codes; the display name lives in `summary` /
  `get_name_display()`.
- Query-count guard tests exist — keep proxy queries bounded.

## Key files
`app/views.py` (`palette`, `search`, `browse_faceted`), `app/browse.py`,
new `catalogue/search.py` + a `reindex_search` command, `app/base_settings.py`
(Typesense config), `resources/js/components/organisms/CommandPalette.vue`
(loading state), `docs/DEPLOYMENT.md` (container + ops). Full spec in #213.

## Open decisions to confirm at kickoff
1. Unified `content` collection vs per-model.
2. Synchronous vs queued indexing (recommend start synchronous).
3. When/whether to roll to prod (legacy-team coordination required).

# Clayton TV

Church media platform (Django + Inertia + Vue 3), shipping through a three-tier
`dev` → `beta` → `main` flow. **Current status, roadmap, epics, and priorities
live in GitHub, not in a doc** — see the [Clayton TV — Delivery board](https://github.com/orgs/Clayton-TV/projects/6)
(Phase = MVP1/MVP2/Backlog/Shipped; Priority = MoSCoW) and the issues/epics it
tracks. To reconstruct current state at any point, read the open issues and the
epic sub-issue rollups. Reference docs for specifics: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
(environments, server, security baseline), [docs/SERVER_AUDIT.md](docs/SERVER_AUDIT.md)
(a dated 2026-06-12 survey, not current state),
[docs/TESTING_NOTES.md](docs/TESTING_NOTES.md) (known data quirks).

## Workflow

- **Three environments, one-directional promotion:** `dev` → `beta` → `main`.
  Each branch has its own environment (https://dev.claytontv.co.uk,
  https://beta.claytontv.co.uk, https://claytontv.co.uk) and its own deploy
  workflow. `main` is the repo default branch and is protected; production
  deploys fire on push to it. Details: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
- **Integration trunk is `dev`.** Feature branches off `dev`
  (`claytontv/<issue>/<slug>`), PR back into `dev` when CI is green. Promote
  `dev` → `beta` → `main`; never branch off or PR straight into `beta`/`main`.
- Don't push directly to `dev`, `beta` or `main` — everything lands by PR.
- **TDD.** Feature-level tests against realistic data. The legacy data is full
  of quirks — never assume column names or content; verify empirically.
- Style: clean code, minimal abstraction, thin views → plain service functions
  → models. Junior-readable beats clever.

## Commands

```bash
uv run poe          # list all tasks
uv run poe dev      # Django + Vite dev servers (or use .claude/launch.json)
uv run poe test     # pytest (coverage gate: 80%, enforced locally + in CI)
uv run poe fix      # ruff lint --fix + format
uv run poe manage <cmd>
npm run build-only  # production asset build
npm run type-check  # vue-tsc against tsconfig.app.json (runs in CI)
```

Local HTTPS: `herd proxy claytontv http://127.0.0.1:8000 --secure` →
https://claytontv.test. Local DB is SQLite; seed it with
`uv run poe manage link_and_import_all` (imports CSV/ — takes a few minutes).

## Architecture notes & traps

- **Inertia v3 client + inertia-django 1.2**: bridged by a project-level
  [templates/inertia.html](templates/inertia.html) override (v3 JSON-script
  protocol). Remove when inertia-django#99 lands. Don't adopt v3 features that
  need new server support (useHttp, once props, infinite scroll). SSR exists
  but is opt-in (`INERTIA_SSR_ENABLED`) until the Headless UI nav is replaced.
- **Video↔relation linking is inconsistent per model — match the importer:**
  topics link via `Video.topic` (count with `Count("video")`), but series link
  via the `Series.videos` M2M (count with `Count("videos")` — the `Video.series`
  FK is never populated). Counting the wrong one silently returns 0. In tests,
  link series with `series.videos.add(video)`, NOT `VideoFactory(series=...)`.
- **Legacy ID→name lookup tables** (speakers/topics/books/series) captured from
  the old admin live in data/legacy_rescue/lookups/ for the Epic 2 importer.
- **Never pass full Video models as Inertia props** — the serializer pulls all
  five M2M relations per video. Use `video_card_props()` (app/cards.py).
- **Importers are destructive** (delete-all-then-reload) until Epic 2 replaces
  them with upserts. Never point them at a database you care about.
- Query counts are a guarded regression:
  tests/test_homepage.py::test_homepage_query_count_does_not_grow_with_catalogue_size.
- SQLite locally vs PostgreSQL on every server environment masks performance
  bugs — sanity check anything query-heavy against the full imported catalogue.

## Environments

Server `app03.tgo.dev` (SSH port 2202, key-only) hosts all three environments.
Layouts, services, per-env Typesense and the deploy flow: docs/DEPLOYMENT.md.
Observability is wired: Sentry (`SENTRY_DSN`, `app/production_settings.py`) →
sentry.tgo.dev, PostHog (`resources/js/lib/analytics.ts`, `VITE_POSTHOG_*` baked
in at build time) → posthog.tgo.dev.

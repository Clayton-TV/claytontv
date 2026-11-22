# Clayton TV

Django + Inertia + Vue 3. Track status, priorities and roadmap in
[GitHub](https://github.com/orgs/Clayton-TV/projects/8).

Reference: [Deployment](docs/DEPLOYMENT.md),
[historical server audit](docs/SERVER_AUDIT.md),
[testing notes](docs/TESTING_NOTES.md).

## Workflow

- Branch from `dev` using `claytontv/<issue>/<slug>`; PR into `dev`.
- Promote by PR through `dev` → `beta` → `main`. Pushes deploy the corresponding
  environment. Do not push directly to shared branches.
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

Local HTTPS (macOS only, needs Laravel Herd):
`herd proxy claytontv http://127.0.0.1:8000 --secure` → https://claytontv.test. Local DB is SQLite; seed it with
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
- **The legacy CSV importers are destructive** (delete-all-then-reload) and are
  local-seed-only. Epic 2 replaced ingestion on real databases with idempotent
  upserts (`catalogue/ingest/`, `ingest_legacy_dump`, `sync_live_admin`), and
  `guard_destructive()` (catalogue/management/commands/_destructive.py) now
  refuses to run the destructive ones against a non-SQLite database unless
  `ALLOW_DESTRUCTIVE_IMPORT=1`. Don't defeat that guard.
- Query counts are a guarded regression:
  tests/test_homepage.py::test_homepage_query_count_does_not_grow_with_catalogue_size.
- SQLite locally vs PostgreSQL on every server environment masks performance
  bugs — sanity check anything query-heavy against the full imported catalogue.

## Environments

Server: `app03.tgo.dev`, SSH port 2202, key authentication.
Paths, services and environment isolation: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
Sentry uses `SENTRY_DSN` and `SENTRY_ENVIRONMENT`; PostHog uses build-time
`VITE_POSTHOG_*` values. Verify configuration on the target environment.

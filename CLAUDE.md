# Clayton TV

Church media platform (Django + Inertia + Vue 3). A major revamp is underway —
**read [docs/MASTER_PLAN.md](docs/MASTER_PLAN.md) first**: it holds the epics,
current status, decision log, and working agreement. Other key docs:
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) (environments, server, security
baseline), [docs/SERVER_AUDIT.md](docs/SERVER_AUDIT.md),
[docs/TESTING_NOTES.md](docs/TESTING_NOTES.md) (known data quirks).

## Workflow

- Trunk for the revamp is the **`beta` branch** → auto-deploys to
  https://beta.claytontv.co.uk on push. `main` belongs to the legacy live-site
  team (Matt, Jonathan) — don't touch it.
- Feature branches off `beta` (`claytontv/<epic-or-issue>/<slug>`), PR back to
  `beta` when CI is green.
- **TDD.** Feature-level tests against realistic data. The legacy data is full
  of quirks — never assume column names or content; verify empirically.
- Style: clean code, minimal abstraction, thin views → plain service functions
  → models. Junior-readable beats clever.

## Commands

```bash
uv run poe          # list all tasks
uv run poe dev      # Django + Vite dev servers (or use .claude/launch.json)
uv run poe test     # pytest (coverage gate: 60%)
uv run poe fix      # ruff lint --fix + format
uv run poe manage <cmd>
npm run build-only  # production asset build (type-check is known-broken, #148)
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
- **Topic and Series each have a decoy `videos` M2M** (`related_name="+"`).
  The app actually queries the reverse of `Video.topic` / `Video.series`.
  Link test data through the Video side (see tests/factories.py).
- **Never pass full Video models as Inertia props** — the serializer pulls all
  five M2M relations per video. Use `video_card_props()` (app/views.py).
- **Importers are destructive** (delete-all-then-reload) until Epic 2 replaces
  them with upserts. Never point them at a database you care about.
- Query counts are a guarded regression:
  tests/test_homepage.py::test_homepage_query_count_does_not_grow_with_catalogue_size.
- SQLite locally vs PostgreSQL on beta/prod masks performance bugs — sanity
  check anything query-heavy against the full imported catalogue.

## Environments

Server `app03.tgo.dev` (SSH port 2202, key-only). Beta and prod layouts,
services, and deploy flow: docs/DEPLOYMENT.md. Observability targets:
sentry.tgo.dev + posthog.tgo.dev (wiring pending, Epic 1 leftover).

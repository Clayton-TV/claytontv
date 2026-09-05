# Clayton TV

Christian media platform built with Django, Inertia and Vue 3.

Feature branches target `dev`. Releases promote through `dev` → `beta` → `main`.
Track work in [GitHub issues](https://github.com/Clayton-TV/claytontv/issues) and the
[project board](https://github.com/orgs/Clayton-TV/projects/8). Team chat:
[Discord](https://discord.gg/Gbh8fWthj).

## Prerequisites

- Git.
- [uv](https://docs.astral.sh/uv/getting-started/installation/). It installs Python
  3.14 from `.python-version` and manages the project environment.
- Node.js 22 and npm. `.nvmrc` selects the supported major version; run
  `nvm install` and `nvm use` if using nvm.
- Docker only for optional local Typesense. Django runs natively with SQLite.

## Local setup

These commands work on macOS, Linux and Windows PowerShell unless indicated.

### 1. Clone and install

```bash
git clone --branch dev https://github.com/Clayton-TV/claytontv.git
cd claytontv
uv sync --locked
npm ci
uv run pre-commit install
```

For SSH authentication, use
`git clone --branch dev git@github.com:Clayton-TV/claytontv.git` instead.
`uv run` uses the project environment; shell activation is unnecessary.

### 2. Configure

```bash
cp .env.example .env
uv run poe generate-key
```

In Windows cmd.exe, use `copy .env.example .env` instead of `cp`.
The key command fills `SECRET_KEY`; retain
`DJANGO_SETTINGS_MODULE=app.local_settings`. Other values have local defaults
or are optional. Server configuration belongs in each environment's
`shared/.env`; see [Deployment](docs/DEPLOYMENT.md).

### 3. Create the database

```bash
uv run poe manage migrate
```

Optional catalogue seed:

```bash
uv run poe manage link_and_import_all
```

The seed imports `CSV/` and **replaces existing catalogue data**. Run it only
against a disposable local database. Do not bypass the non-SQLite guard with
`ALLOW_DESTRUCTIVE_IMPORT`.

### 4. Start development servers

```bash
uv run poe dev
```

Open http://127.0.0.1:8000. This starts Django and Vite together.

For optional local HTTPS with Laravel Herd on macOS:

```bash
herd proxy claytontv http://127.0.0.1:8000 --secure
```

Then open https://claytontv.test.

### 5. Enable Typesense (optional)

Search falls back to the database without Typesense. To test Typesense locally,
set `TYPESENSE_API_KEY=dev-typesense-key` in `.env`, then run:

```bash
docker compose up -d typesense
uv run poe manage reindex_search
```

Wait for the container to start before indexing. Stop it with
`docker compose down`. Alternatively, `uv run poe typesense` runs the container
in the foreground; use a second terminal for indexing.

The compose file is local-only. Server environments need separate instances
and configuration; see [Deployment](docs/DEPLOYMENT.md).

## Development commands

```bash
uv run poe manage <cmd>   # Django management command
uv run poe test           # Python tests and 80% coverage gate
uv run poe lint-check
uv run poe format-check
uv run poe fix            # apply Ruff fixes and formatting
npm run type-check
npm run lint-check
npm run format-check
npm run test:unit
npm run build-only
```

Pre-commit runs Ruff, Gitleaks and frontend hooks. Install frontend dependencies
with `npm ci` before committing. Run all hooks with:

```bash
uv run pre-commit run --all-files --show-diff-on-failure
```

## Troubleshooting

- **uv not found:** restart the shell after installation and check `PATH`.
- **Frontend tests fail:** check `node --version` is 22, then run `npm ci`.
- **Missing settings or secret key:** check `.env` exists, retains
  `DJANGO_SETTINGS_MODULE`, and contains a generated `SECRET_KEY`.
- **Empty catalogue:** seed the disposable local database as described above.
- **Typesense unavailable:** check the container, matching API key and index.
  Database search remains available when Typesense is unconfigured or unreachable.
- **Pre-commit cannot find frontend tools:** run `npm ci` in this checkout.

## Stack

- Python 3.14, Django 6 and inertia-django.
- SQLite locally; PostgreSQL for server deployments.
- Vue 3, TypeScript, Vite, Tailwind CSS 4 and shadcn-vue.
- Optional Typesense search with a database fallback.

## Contribution workflow

1. Assign yourself an issue when actively working on it. Branch from `dev`
   using `claytontv/<issue>/<slug>` and keep each PR to one change.
2. Run local checks and open a PR into `dev`. Merges deploy to
   https://dev.claytontv.co.uk.
3. Promote `dev` to `beta` by PR; verify at https://beta.claytontv.co.uk.
   Anyone may review beta changes. Check for pending production promotion before
   adding another feature.
4. Promote `beta` to `main` by PR. Merges deploy to https://claytontv.co.uk.
   Production approval follows the team's JG/FT/MB/JS convention; this is not an
   exclusive reviewer restriction enforced by GitHub.

Deployment procedures: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Write issues in plain English and set their type and labels. Feature ideas are
triaged with Ettie at hackathons; consult Caitlin or Ettie before starting
untriaged work.

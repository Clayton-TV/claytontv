# Clayton TV

A church media platform — Christian video you can trust, simple enough for an
elderly congregant on a phone and deep enough for a minister researching a
passage. Django + Inertia + Vue 3, currently being rebuilt on the `beta` branch.

New here? This README gets you running locally in a few minutes. To see what's
being worked on and what's planned, browse the
[issues and project board](https://github.com/Clayton-TV/claytontv/issues).

Works the same on **macOS, Windows, and Linux**: uv pins the Python version and
locks every dependency, so you get an identical environment without Docker. The
app itself runs natively (the same way the beta/production servers run it) —
Docker is only ever needed for the optional local search engine (step 7). Where a
command differs on Windows, the PowerShell variant is shown alongside it.

## Prerequisites

- **Python** — installed for you by uv (3.14, pinned in `.python-version`). No
  pyenv or system Python required.
- **Node.js 22+ and npm** — for the Vue/Vite frontend. Install from
  [nodejs.org](https://nodejs.org), or with a version manager such as
  [nvm](https://github.com/nvm-sh/nvm) (`nvm install 22`) or
  [fnm](https://github.com/Schniz/fnm). npm ships with Node.
- **Git**.
- **Docker** — *optional*, only for running a local Typesense search container
  (step 7). The app runs fine without it; search falls back to the database.

## 1. Clone the repository

```bash
git clone git@github.com:clayton-tv/claytontv.git
cd claytontv
```

## 2. Install uv

The project uses [uv](https://docs.astral.sh/uv/) for Python and dependency
management. uv installs the right Python automatically.

```bash
# macOS / Linux / WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 3. Install dependencies

Python (and the dev tools), then the frontend packages:

```bash
uv sync                  # creates .venv/ and installs locked Python deps
uv run pre-commit install
npm install              # Vue / Vite / Tailwind frontend deps
```

> `uv run` always uses the project venv — there is nothing to "activate". If you
> prefer shorter commands, activate it once per shell and drop the `uv run`
> prefix: `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\Activate.ps1`
> (Windows PowerShell).

## 4. Set up the environment

Copy the example file, then generate a secret key into it:

```bash
cp .env.example .env          # macOS / Linux / WSL
copy .env.example .env        # Windows PowerShell
uv run poe generate-key       # writes a SECRET_KEY into .env
```

That's all you need to run the app. The defaults work out of the box; everything
else in `.env.example` is optional and grouped by purpose:

- **Required** — `SECRET_KEY` (filled by `generate-key`), `DEBUG`,
  `DJANGO_SETTINGS_MODULE` (local dev settings).
- **Vite** — `VITE_HOST` / `VITE_PORT`; leave as-is unless the port clashes.
- **Typesense search** *(optional)* — `TYPESENSE_*`. Leave empty to use the
  database-backed search; fill them in only if you run the search container
  (step 7).
- **Observability** *(optional)* — `SENTRY_*` / `VITE_POSTHOG_*`. Leave empty
  locally; these are set on servers / CI.
- **Legacy admin sync** *(optional)* — `LEGACY_ADMIN_*`, used only by the
  catalogue sync cron. Leave empty for normal local dev.

## 5. Set up the database

The local database is SQLite — no server to install. Apply the migrations:

```bash
uv run poe manage migrate
```

Optionally seed it with the legacy catalogue (imports the CSVs under `CSV/` —
takes a few minutes). This is **destructive** (delete-all-then-reload), so only
ever run it against a local database you don't mind wiping:

```bash
uv run poe manage link_and_import_all
```

## 6. Run the application

We use [Poe the Poet](https://poethepoet.natn.io/) as a task runner; it
self-documents the useful commands:

```bash
uv run poe          # list all tasks
uv run poe dev      # run Django + Vite together (the usual dev loop)
```

`uv run poe dev` starts the Django server and the Vite dev server side by side.
Open the app at the Django URL (http://localhost:8000) — Vite (port 5173) only
serves frontend assets.

### Local HTTPS (optional, macOS)

With [Laravel Herd](https://herd.laravel.com) installed you can proxy the dev
server behind trusted local HTTPS:

```bash
herd proxy claytontv http://127.0.0.1:8000 --secure
# → https://claytontv.test
```

## 7. Search (optional): local Typesense via Docker

Search works without any extra setup — it falls back to the database. To develop
against the same engine the servers use, run a local [Typesense](https://typesense.org)
container. This is the only part of local dev that needs Docker.

```bash
# 1. Set TYPESENSE_API_KEY in .env (any value; the compose default is dev-typesense-key)
uv run poe typesense              # = docker compose up typesense (bound to loopback)
uv run poe manage reindex_search  # build the index from the local database
```

The container is for local development only — beta/production run their own
persistent Typesense provisioned on the server (see
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)). Background and operational detail live in
[docs/TYPESENSE_HANDOVER.md](docs/TYPESENSE_HANDOVER.md).

## 8. Everyday commands

```bash
uv run poe manage <cmd>   # any Django management command
uv run poe test           # pytest suite
uv run poe fix            # ruff lint --fix + format
uv run poe lint-check     # lint without fixing (CI parity)
uv run poe format-check   # format check (CI parity)
uv run poe typesense      # start the local Typesense container (optional, step 7)
uv run poe manage reindex_search   # rebuild the search index
npm run build-only        # production frontend build
```

Pre-commit hooks (ruff + gitleaks) run automatically on commit; run them
manually with:

```bash
uv run pre-commit run --all-files --show-diff-on-failure
```

## 9. Troubleshooting

- **`uv: command not found`** — uv isn't on your `PATH` yet. Restart the shell
  after installing, or `source $HOME/.local/bin/env` (macOS/Linux).
- **`npm: command not found` or Vite errors** — Node isn't installed or is too
  old. Check with `node --version` (need 22+) and re-run `npm install`.
- **Blank page / missing styles in the browser** — make sure both servers are
  running via `uv run poe dev`, and open the Django URL (port 8000), not Vite's
  port 5173.
- **`SECRET_KEY` / settings errors on startup** — you skipped step 4. Confirm
  `.env` exists and that `uv run poe generate-key` populated `SECRET_KEY`.
- **No videos / empty catalogue** — the database hasn't been seeded. Run
  `uv run poe manage link_and_import_all` (step 5).
- **Search returns nothing / not using Typesense** — the container isn't running
  or `TYPESENSE_API_KEY` in `.env` doesn't match it. With no working Typesense,
  search silently falls back to the database (no error). Start it with
  `uv run poe typesense`, then `uv run poe manage reindex_search` (step 7).
- **Windows: `cp` / `source` "not recognized"** — those are macOS/Linux commands.
  Use `copy .env.example .env` and `.venv\Scripts\Activate.ps1` instead.
- **Frontend deps fail to install on Linux/CI** — platform-specific binaries are
  declared as `optionalDependencies`; a clean `npm install` resolves them.

## 10. Stack at a glance

- **Backend:** Python 3.14, Django 6, Inertia (inertia-django), SQLite locally /
  PostgreSQL in production
- **Search:** Typesense (optional locally), with a database fallback
- **Frontend:** Vue 3 + TypeScript + Vite + Tailwind CSS 4, shadcn-vue (reka-ui)
- **Quality:** ruff, pytest (+pytest-django), oxlint/eslint/prettier, pre-commit,
  gitleaks

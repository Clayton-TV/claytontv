# Clayton TV

A church media platform — Christian video you can trust, simple enough for an
elderly congregant on a phone and deep enough for a minister researching a
passage. Django + Inertia + Vue 3, currently being rebuilt on the `beta` branch.

New here? This README gets you running locally in a few minutes. To see what's
being worked on and what's planned, browse the
[issues and project board](https://github.com/Clayton-TV/claytontv/issues).

## Prerequisites

- **Python** — installed for you by uv (3.14, pinned in `.python-version`). No
  pyenv or system Python required.
- **Node.js 22+ and npm** — for the Vue/Vite frontend. Install from
  [nodejs.org](https://nodejs.org), or with a version manager such as
  [nvm](https://github.com/nvm-sh/nvm) (`nvm install 22`) or
  [fnm](https://github.com/Schniz/fnm). npm ships with Node.
- **Git**.

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
> prefer shorter commands, `source .venv/bin/activate` once per shell and drop
> the `uv run` prefix.

## 4. Set up the environment

```bash
cp .env.example .env
uv run poe generate-key   # writes a SECRET_KEY into .env
```

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

## 7. Everyday commands

```bash
uv run poe manage <cmd>   # any Django management command
uv run poe test           # pytest suite
uv run poe fix            # ruff lint --fix + format
uv run poe lint-check     # lint without fixing (CI parity)
uv run poe format-check   # format check (CI parity)
npm run build-only        # production frontend build
```

Pre-commit hooks (ruff + gitleaks) run automatically on commit; run them
manually with:

```bash
uv run pre-commit run --all-files --show-diff-on-failure
```

## 8. Troubleshooting

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
- **Frontend deps fail to install on Linux/CI** — platform-specific binaries are
  declared as `optionalDependencies`; a clean `npm install` resolves them.

## 9. Stack at a glance

- **Backend:** Python 3.14, Django 6, Inertia (inertia-django), SQLite locally /
  PostgreSQL in production
- **Frontend:** Vue 3 + TypeScript + Vite + Tailwind CSS 4, shadcn-vue (reka-ui)
- **Quality:** ruff, pytest (+pytest-django), oxlint/eslint/prettier, pre-commit,
  gitleaks

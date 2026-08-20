# Clayton TV

A church media platform — Christian video you can trust, simple enough for an
elderly congregant on a phone and deep enough for a minister researching a
passage. Django + Inertia + Vue 3.

Work ships through three environments — `dev` → `beta` → `main` — each with its
own site and deploy workflow. Branch off `dev`, PR back into `dev`; see
[Development Procedures](#development-procedures) below and
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the server-side detail.

New here? This README gets you running locally in a few minutes. To see what's
being worked on and what's planned, browse the
[issues](https://github.com/Clayton-TV/claytontv/issues) and the
[project board](https://github.com/orgs/Clayton-TV/projects/6) (org project —
only visible to the Clayton TV developer team). Day-to-day chat is on
[Discord](https://discord.gg/Gbh8fWthj), also team-only.

Works the same on **macOS, Windows, and Linux**: uv pins the Python version and
locks every dependency, so you get an identical environment without Docker. The
app itself runs natively (the same way the servers run it) — Docker is only ever
needed for the optional local search engine (step 7). Where a command differs on
Windows, the variant is shown alongside it.

## Prerequisites

- **Python** — installed for you by uv (3.14, pinned in `.python-version`). No
  pyenv or system Python required.
- **Node.js 22+ and npm** — for the Vue/Vite frontend. The version is pinned in
  `.nvmrc`, so with a version manager such as [nvm](https://github.com/nvm-sh/nvm)
  or [fnm](https://github.com/Schniz/fnm) just run `nvm use` / `fnm use` in the
  repo to select it (`nvm install` first if you don't have it). Otherwise install
  Node 22 from [nodejs.org](https://nodejs.org). npm ships with Node.
- **Git**.
- **Docker** — *optional*, only for running a local Typesense search container
  (step 7). The app runs fine without it; search falls back to the database.
  Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) on
  macOS or Windows (on Windows, enable the **WSL2 backend** — Docker Desktop
  offers it during setup and it needs WSL2 installed:
  `wsl --install` in an elevated PowerShell), or Docker Engine from your
  distribution's packages on Linux.

## 1. Clone the repository

Pick **one** of these. SSH needs a key on your GitHub account; HTTPS doesn't
(Git will prompt for your credentials).

```bash
git clone git@github.com:clayton-tv/claytontv.git      # SSH
```

```bash
git clone https://github.com/Clayton-TV/claytontv.git  # HTTPS
```

Then:

```bash
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

On macOS, Linux, WSL **or PowerShell** (where `cp` is a built-in alias for
`Copy-Item`):

```bash
cp .env.example .env
```

On Windows **cmd.exe**, where `cp` doesn't exist:

```
copy .env.example .env
```

Then, in any shell:

```bash
uv run poe generate-key       # writes a SECRET_KEY into .env
```

That's all you need to run the app. `SECRET_KEY` is the only value you must
fill in, and `generate-key` does it for you; `DJANGO_SETTINGS_MODULE` must stay
set (nothing supplies a default), and everything else already has a working
local default. `.env.example` is grouped and commented for local dev — read it
there rather than here, so the two can't drift. The optional groups (Typesense
search, Sentry/PostHog observability, legacy admin sync) can all be left empty.
Server-only settings (`DATABASE_URL`, `REDIS_URL`, `YOUTUBE_API_KEY`, the
`OLLAMA_*` block and friends) aren't in the example file at all — see
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for those.

## 5. Set up the database

The local database is SQLite — no server to install. Apply the migrations:

```bash
uv run poe manage migrate
```

Optionally seed it with the legacy catalogue (imports the CSVs under `CSV/` —
takes a few minutes). This is **destructive** (delete-all-then-reload), so only
ever run it against a local database you don't mind wiping. A guard
(`guard_destructive()`) refuses to run it against anything other than SQLite
unless `ALLOW_DESTRUCTIVE_IMPORT=1` is set — don't set that locally:

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

First set `TYPESENSE_API_KEY` in `.env` (any value; the compose default is
`dev-typesense-key`). Then start the container and build the index:

```bash
uv run poe typesense              # = docker compose up typesense (bound to loopback)
```

`uv run poe typesense` runs in the **foreground** and holds the terminal —
leave it running and open a second terminal for the next command. If you'd
rather have it in the background, run the detached form instead of the poe task:

```bash
docker compose up -d typesense    # detached; stop later with `docker compose down`
```

Either way, build the index once the container is up:

```bash
uv run poe manage reindex_search  # build the index from the local database
```

This container is for local development only. On the servers, **dev and beta
each run their own persistent Typesense** provisioned under the environment's
`shared/typesense/`; **production is not provisioned yet** and falls back to
database search (see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)). Background and
operational detail live in
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
npm run type-check        # vue-tsc — CI runs this, so run it before pushing
```

Pre-commit hooks run automatically on commit: ruff (lint + format) and gitleaks,
plus **local `prettier` and `eslint` hooks** that shell out to `npm run format`
and `npm run lint`. Those two are `language: system`, so they need
`node_modules` — in a fresh clone or a fresh worktree where you haven't run
`npm install` yet, they fail with **exit code 127** ("command not found") and
block the commit. Run `npm install` (step 3) before your first commit.

Run the hooks manually with:

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
- **Windows: `source` "not recognized"** — `source` is a Unix shell builtin with
  no PowerShell equivalent by that name; PowerShell dot-sources with
  `. .\path\to\script.ps1`. For the virtualenv specifically you don't need it at
  all — just run `.venv\Scripts\Activate.ps1`.
- **Windows: `Activate.ps1` "cannot be loaded because running scripts is
  disabled"** — Windows client editions default to a `Restricted` execution
  policy. Either allow scripts for the current session with
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and re-run it, or
  use `.venv\Scripts\activate.bat` from cmd.exe. (Or skip activation entirely —
  `uv run` needs none of this.)
- **Windows: `cp` "not recognized"** — this happens in **cmd.exe**, not
  PowerShell. In PowerShell `cp` is a built-in alias for `Copy-Item` and works
  fine (as does `copy`). In cmd.exe use `copy .env.example .env`.
- **Pre-commit fails with exit code 127** — the local `prettier` / `eslint`
  hooks can't find `npm`'s binaries. Run `npm install` (step 3) in this
  checkout, then commit again.
- **Frontend deps fail to install on Linux/CI** — platform-specific binaries are
  declared as `optionalDependencies`; a clean `npm install` resolves them.

## 10. Stack at a glance

- **Backend:** Python 3.14, Django 6, Inertia (inertia-django), SQLite locally /
  PostgreSQL on every server environment
- **Search:** Typesense (optional locally), with a database fallback
- **Frontend:** Vue 3 + TypeScript + Vite + Tailwind CSS 4, shadcn-vue (reka-ui)
- **Quality:** ruff, pytest (+pytest-django), oxlint/eslint/prettier, pre-commit,
  gitleaks

## Development Procedures

### Branch Process

Promotion is one-directional: **feature branch → `dev` → `beta` → `main`**.
Nothing skips a tier, and nothing reaches a shared environment except by PR.

### 1. Feature Branches
- Set purpose
- Single issue/single feature/single bug
- Ideally attach to an issue and give a name that references the issue
  (`claytontv/<issue>/<slug>`)
- Branch off `dev`
- Test features locally, then PR into `dev`
### 2. Dev
- Integration environment (https://dev.claytontv.co.uk) — shared, so work
  reaches it **by merging your PR into `dev`**, never by deploying a feature
  branch to it
- Deploys on push to `dev`; the workflow can also be re-run by hand
  (`workflow_dispatch`) from the Actions tab
### 3. Beta
- Beta site (https://beta.claytontv.co.uk) — promoted by PR from `dev`;
  autodeploys on push to `beta`
- Anyone can approve a PR
- Test your changes live
- Before opening the PR (there is no PR template in the repo yet — do these by
  hand)
  - confirm you've tested locally
  - check there isn't already a lag between beta & production
- One new feature at a time
  - PR to Production before the next feature PR is accepted to prevent backlog
### 4. Production branch (`main`)
- live site (https://claytontv.co.uk) — promoted by PR from `beta`; auto-deploys
  on push to `main` (treat with care!)
- by convention only 4 approvers (JG, FT, MB, JS) — a convention, not a
  configured rule: branch protection on `main` requires one approving review,
  but there is no `CODEOWNERS` file, so any reviewer with write access can
  approve. Don't rely on GitHub to enforce this.
  - Testing protocol

### Issue Process
### 1. Issue Creation
- Plain English - make sure content and updates can be understood by all
- Fill in issue type & tags
- If you have a feature idea
  - make an issue
  - at each hackathon we’ll triage & check them with client (Ettie)
  - if you want to work on a feature/issue before triage, run it by Caitlin/Ettie
### 2. Issue Assigning
- Only assign if actively working (not future work), to prevent blocking
- If you're working on an issue
  - Assign it to yourself
  - Make a branch & name it to match






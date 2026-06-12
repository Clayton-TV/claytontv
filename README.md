# Clayton TV

Clayton TV provides Christian media you can trust.

> The revamp roadmap lives in [docs/MASTER_PLAN.md](docs/MASTER_PLAN.md).

## 1. Clone the repository

```bash
git clone git@github.com:clayton-tv/claytontv.git
cd claytontv
```

## 2. Install uv

The project uses [uv](https://docs.astral.sh/uv/) for Python and dependency
management. uv installs the right Python (3.14, pinned in `.python-version`)
automatically — no pyenv or system Python required.

```bash
# macOS / Linux / WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 3. Install dependencies

```bash
uv sync
uv run pre-commit install
```

This creates `.venv/`, installs all locked dependencies (including dev tools),
and sets up the pre-commit hooks.

## 4. Set up the environment

```bash
cp .env.example .env
uv run poe generate-key   # writes a SECRET_KEY into .env
```

## 5. Run the application

We use [Poe the Poet](https://poethepoet.natn.io/) as a task runner; it
self-documents the useful commands:

```bash
uv run poe          # list all tasks
uv run poe dev      # run Django + Vite together (the usual dev loop)
```

> Tip: `uv run` always uses the project venv — there is nothing to "activate".
> If you prefer shorter commands, `source .venv/bin/activate` once per shell
> and drop the `uv run` prefix.

### Local HTTPS (optional, macOS)

With [Laravel Herd](https://herd.laravel.com) installed you can proxy the dev
server behind trusted local HTTPS:

```bash
herd proxy claytontv http://127.0.0.1:8000 --secure
# → https://claytontv.test
```

## 6. Everyday commands

```bash
uv run poe manage <cmd>   # any Django management command
uv run poe test           # pytest suite
uv run poe fix            # ruff lint --fix + format
uv run poe lint-check     # lint without fixing (CI parity)
uv run poe format-check   # format check (CI parity)
```

Pre-commit hooks (ruff + gitleaks) run automatically on commit; run them
manually with:

```bash
uv run pre-commit run --all-files --show-diff-on-failure
```

## 7. Stack at a glance

- **Backend:** Python 3.14, Django 6, Inertia (inertia-django), SQLite locally /
  PostgreSQL in production
- **Frontend:** Vue 3 + TypeScript + Vite + Tailwind CSS 4, shadcn-vue (reka-ui)
- **Quality:** ruff, pytest (+pytest-django), oxlint/eslint/prettier, pre-commit,
  gitleaks

# Deployment

Deployments use `app03.tgo.dev`, a shared server also hosting unrelated sites.
Workflow configuration is recorded below; verify provisioned services and
credentials on the target environment before changing them. Team overview:
[Environments and Deployments](https://github.com/Clayton-TV/claytontv/wiki/Environments-and-Deployments).

| | Dev | Beta | Production |
|---|---|---|---|
| URL | https://dev.claytontv.co.uk | https://beta.claytontv.co.uk | https://claytontv.co.uk |
| Branch | `dev` | `beta` | `main` (default) |
| Workflow | `deploy-to-dev.yaml` | `deploy-to-beta.yaml` | `deploy-to-production.yaml` |
| Root | `/srv/dev-claytontv` | `/srv/beta-claytontv` | `/srv/claytontv` |
| Service | `gunicorn-claytontv-dev.service` | `gunicorn-claytontv-beta.service` | `gunicorn-claytontv.service` |
| Socket under `shared/run/` | `claytontv-dev.sock` | `claytontv-beta.sock` | `claytontv.sock` |
| Database | `claytontv_dev` | `claytontv_beta` | `claytontv` |

Each environment requires a separate PostgreSQL database/role, Redis database,
Typesense instance, `.env`, media directory and Gunicorn service/socket.
Set `DATABASE_URL`, `REDIS_URL`, `TYPESENSE_*` and `SENTRY_ENVIRONMENT` explicitly.
The Redis default is database 1; the Sentry environment default is `beta`.

Release layout:
`releases/<timestamp>` + `current` symlink + `shared/{.env,media,logs,run,backups}`.
Provision these shared directories before the first deploy. The deploy account
needs ownership of its release directories and permission to restart the
corresponding Gunicorn services. Existing installations use the Linux `dev` user.

## Deploy flow

Promote by PR: feature branch → `dev` → `beta` → `main`. Each environment
workflow runs on pushes to its branch and supports manual `workflow_dispatch`.
All callers use [deploy.yaml](../.github/workflows/deploy.yaml), with environment
paths, service, URL and secrets supplied separately.

CI and deployment run independently; deployment does not wait for CI success.
The required CI checks are Quality Assurance, Frontend Checks and Unit Tests.
See [ci.yaml](../.github/workflows/ci.yaml) for current triggers and commands.

The shared workflow:

1. Installs npm dependencies and builds assets, including configured PostHog values.
2. Copies the release to the server, excluding secrets and local dependencies.
3. Runs `uv sync --locked --no-dev`, links shared environment/media, and collects static files.
4. Runs `pg_dump | gzip`, retaining seven backups, then applies migrations.
5. Runs `reindex_search`; all three callers currently enable this step.
6. Switches the `current` symlink, restarts Gunicorn and retains five releases.
7. Requires an HTTP 200 from the environment URL.

The runtime uses Python 3.14, selected by `.python-version`.

Failure behaviour:

- The backup directory must exist. The script lacks `pipefail`, so a failed
  `pg_dump` can be masked by successful `gzip` and migration may proceed.
  Validate backups before relying on them for recovery.
- Unconfigured or unreachable Typesense fails reindexing before the symlink
  switch. The previous release stays selected, but migrations may already have run.
- The HTTP smoke test checks availability only; verify rendered pages after release.

For a manual redeploy, dispatch the relevant environment workflow.

`close-issues-on-beta-merge.yaml` reads closing keywords from PRs merged into
`beta`. Feature PRs targeting `dev` do not close their issues automatically;
include closing references in the promotion PR or close them when verified.

Operational examples below use beta paths and services. Substitute the target
Root and Service from the table; check environment-specific configuration first.

## Server security baseline (set 2026-06-12)

- sshd: key-auth only, no root login — enforced by
  `/etc/ssh/sshd_config.d/00-hardening.conf` (must stay lexically FIRST:
  OpenSSH keeps the first value per option, and cloud-init's 50- file sets
  `PasswordAuthentication yes`).
- SSH listens on 2202 only (socket-activated); ufw: default-deny, allows
  80/443, rate-limits 2202.
- fail2ban: sshd jail (aggressive, watches `ssh.service` journal — NOT the
  Debian-default `sshd.service`) + nginx-bad-request jail.
- 4 GB swapfile, swappiness 10.
- unattended-upgrades handles security patches; full apt upgrades are manual
  (quiet-hour, other sites share the box).
- **nginx default-deny (added 2026-06-14):** `sites-enabled/00-default-deny` is
  the `default_server` on 80 + 443 (snakeoil cert) and `return 444`s any request
  whose Host/SNI matches no real vhost. Vulnerability scanners hammer the box on
  its raw Contabo hostname (`vmi2435506.contaboserver.net`) / bare IP probing for
  leaked secrets (`/build/.env`, `/mail/sendgrid.env`, wp-/phpMyAdmin paths); these
  used to fall through to beta's vhost → Django → a flood of `DisallowedHost`
  Sentry errors (issue #240, 600+ events). They're now dropped at the edge before
  any app sees them — real vhosts match by `server_name` and are untouched. Verify:
  `curl -s -o /dev/null -w "%{http_code}" --resolve vmi2435506.contaboserver.net:443:161.97.139.3 https://vmi2435506.contaboserver.net/` → `000` (closed); the
  real domains still return 200.
  - **Follow-up hardening (not yet done — see the GH "server hardening v2" issue):**
    a fail2ban jail to ban *direct* scanner IPs hitting malicious paths in
    `access.log` (must keep **Cloudflare ranges in `ignoreip`** — some scan traffic
    arrives via CF IPs, so naive banning would block real CF-fronted users);
    evaluate putting beta/prod behind Cloudflare; consider CrowdSec.

## Legacy admin incremental sync (Epic 2.3)

While clayton.tv survives, beta stays current via `sync_live_admin` (cron,
hourly): it pulls the newest-modified programmes from the legacy admin and
feeds them through the same idempotent upsert core as the dump ingest.

Auth (preferred, self-healing): set `LEGACY_ADMIN_USERNAME` and
`LEGACY_ADMIN_PASSWORD` in `/srv/beta-claytontv/shared/.env` (operator-set;
inject from 1Password via `op run` if preferred) — the sync mints its own
sessions and re-logins automatically when they lapse. Fallback: paste a
logged-in browser's Cookie header as `LEGACY_ADMIN_COOKIE` (expires; fails
loudly when it does). Cron (dev user):

    17 * * * * cd /srv/beta-claytontv/current && .venv/bin/python manage.py sync_live_admin >> /srv/beta-claytontv/shared/logs/sync.log 2>&1

With no --pages flag the sync sizes itself: it pages the newest-modified
list until a whole page is programmes we already hold, so backlogs of any
size (including a first-ever catch-up) self-heal — at ~2-3s per programme
a big catch-up can take a couple of hours. Each page ingests as it
completes, so an interrupted run keeps its progress. Note the meta form
no longer carries the video link; the sync follows the programme's
image-picker media id to mediaUpdate.asp for it (layout observed
2026-06-12).

## YouTube live-stream sync (Epic 4)

`sync_live_streams` keeps the homepage's live/next-service slot honest from
the YouTube Data API. Two cadences (quota: search costs 100 units/call
against 10k/day; status refreshes cost 1):

    # hourly discovery (search for new/scheduled broadcasts)
    7 * * * *   cd /srv/beta-claytontv/current && .venv/bin/python manage.py sync_live_streams --discover >> /srv/beta-claytontv/shared/logs/sync.log 2>&1
    # frequent cheap status refresh (upcoming → live → ended)
    */5 * * * * cd /srv/beta-claytontv/current && .venv/bin/python manage.py sync_live_streams >> /srv/beta-claytontv/shared/logs/sync.log 2>&1

Auth: `YOUTUBE_API_KEY` in `/srv/beta-claytontv/shared/.env` — an API key
from the `tgosolutionsltd` Google Cloud project, restricted to the YouTube
Data API v3 (mint with `gcloud services api-keys create
--display-name=claytontv-livestreams
--api-target=service=youtube.googleapis.com`). Without the key the command
logs a warning and exits 0, so the cron can be armed first. Channels are
discovered from the catalogue's own recent livestream videos — nothing to
configure when the church changes channels.

## Video duration harvest (Epic 4)

`harvest_durations` fills `Video.duration_seconds` from the hosting
platforms — YouTube `videos.list` contentDetails (batched, ~1 unit/50) and
Vimeo oEmbed (no auth). Never touches the legacy admin. Idempotent
(null-only; `--refresh` re-fetches). Recommended daily cron (not yet
installed — add when ready):

    37 4 * * * cd /srv/beta-claytontv/current && .venv/bin/python manage.py harvest_durations >> /srv/beta-claytontv/shared/logs/durations.log 2>&1

Coverage note: YouTube resolves fully; Vimeo resolves only where the stored
URL carries its privacy hash (or the video is public). Hashless older Vimeo
videos stay null until re-synced from the admin (mediaUpdate.asp exposes
MediaDuration in ms) or a Vimeo API token is configured.

## AI content enrichment (Epic #201)

`enrich_catalogue` walks the catalogue and stores AI-proposed metadata
(summary, topics, audience, Bible passages, keywords) in a `VideoEnrichment`
row per video, via a self-hosted Ollama model. The values fold **invisibly**
into the Typesense search `text` (recall boost) — nothing surfaces publicly
unless `AI_ENRICHMENT_PUBLIC` is set (default off). It never touches
human-authored `Video` fields and never touches the legacy admin.

**Resumable + idempotent.** Only enriches videos with no enrichment (or one
from an older `PROMPT_VERSION`), so a cron re-run continues where it left off;
a finished catalogue is a near-instant no-op. `--refresh` re-does everything.
Per-video failures are logged and skipped (retried next run), never fatal.

**Model host.** The model runs on `tgoml` (RTX 5090) and is reached over
tailscale via `OLLAMA_HOST` (see the `OLLAMA` block in `app/base_settings.py`).
Beta's `shared/.env` sets `OLLAMA_HOST=http://100.81.40.52:11434`,
`OLLAMA_MODEL=gemma4:31b-it-qat` (31b only — the 26b MoE degenerates),
`OLLAMA_TIMEOUT=120`. app03 is on the tailnet (peer `100.81.40.52`); sanity-check
with `curl -s $OLLAMA_HOST/api/tags`. Measured throughput **~2.5 s/video** → the
~10k catalogue is **~7 h flat-out**, or ~12–15 h under a polite throttle.

**Single flock-guarded entry point.** Both the off-peak cron and any manual /
pre-fill run go through `/srv/beta-claytontv/shared/enrich_run.sh`, which wraps
`enrich_catalogue` in `flock -n` so the two can **never overlap** (the GPU is
single + serial). Because the command is DB-idempotent (only videos lacking a
current-`PROMPT_VERSION` enrichment), a skipped or interrupted run loses nothing.
The wrapper:

```bash
#!/usr/bin/env bash
# /srv/beta-claytontv/shared/enrich_run.sh — flock-guarded enrichment runner.
LOCK=/srv/beta-claytontv/shared/enrich.lock
cd /srv/beta-claytontv/current || exit 1
flock -n -E 99 "$LOCK" .venv/bin/python manage.py enrich_catalogue "$@"
rc=$?
[ "$rc" -eq 99 ] && echo "$(date -Is) enrich: skipped — a run is already in progress"
exit "$rc"
```

**Off-peak cron (installed, `dev` crontab):**

    23 1 * * * /srv/beta-claytontv/shared/enrich_run.sh --sleep 2 --max-runtime 3600 >> /srv/beta-claytontv/shared/logs/enrich.log 2>&1

**One-off / pre-fill** (detached, survives logout; flat-out shown):

    setsid bash -c '/srv/beta-claytontv/shared/enrich_run.sh --sleep 0 --progress-every 100 >> /srv/beta-claytontv/shared/logs/enrich.log 2>&1' </dev/null &

Enrichment saves fire the search signal, so each enriched video is re-indexed as
it's stored — no separate `reindex_search` needed for the fold-in to take effect.

**Future:** an async Redis job queue (replacing cron dispatch, enabling on-demand
+ import/export jobs) is deferred to its own epic — see #302. Not needed for this
GPU-bound, serial fill.

## Typesense search (#213)

Search (`/search`, the ⌘K palette `/api/palette`) is served by a **self-hosted
Typesense** container with a **graceful ORM fallback** — if Typesense is
unconfigured or unreachable, the views fall back to ORM `icontains` and search
keeps working (the failure is logged + sent to Sentry). So the container is a
performance/quality layer, not a hard dependency.

**Where it lives.** A persistent compose project at
`/srv/beta-claytontv/shared/typesense/` (NOT a per-deploy release dir, so it
survives deploys):

```yaml
# /srv/beta-claytontv/shared/typesense/docker-compose.yml
name: claytontv-beta-search
services:
  typesense:
    image: typesense/typesense:28.0
    restart: unless-stopped
    ports:
      - "127.0.0.1:8108:8108"   # loopback ONLY — Django is the sole client
    environment:
      TYPESENSE_DATA_DIR: /data
      TYPESENSE_API_KEY: ${TYPESENSE_API_KEY}
      TYPESENSE_ENABLE_CORS: "false"
    volumes:
      - typesense-beta-data:/data
volumes:
  typesense-beta-data:
```

- **Bound to `127.0.0.1:8108` only** — never exposed off-box; **do not open 8108
  in ufw**. The API key lives in `shared/typesense/.env` (compose) and is
  mirrored into the app's `shared/.env` as `TYPESENSE_API_KEY` (+
  `TYPESENSE_HOST=127.0.0.1`, `TYPESENSE_PORT=8108`, `TYPESENSE_PROTOCOL=http`).
- Docker installed from the Ubuntu repo (`docker.io` + `docker-compose-v2`),
  service `enabled`; container `restart: unless-stopped` → both survive reboots.

**Provisioning (one-off, as a sudo user — the `dev` deploy user can't manage
Docker):**

```bash
sudo apt-get install -y docker.io docker-compose-v2 && sudo systemctl enable --now docker
# create shared/typesense/{docker-compose.yml,.env}; put a fresh key (openssl rand -hex 32)
# in shared/typesense/.env AND append TYPESENSE_* to shared/.env
cd /srv/beta-claytontv/shared/typesense && sudo docker compose up -d
```

**Ops:**

```bash
TS=/srv/beta-claytontv/shared/typesense
sudo docker compose -f $TS/docker-compose.yml ps          # status
sudo docker compose -f $TS/docker-compose.yml logs -f     # logs
sudo docker compose -f $TS/docker-compose.yml restart     # restart
curl -s http://127.0.0.1:8108/health                      # → {"ok":true}

# Rebuild the index from the DB (drop + recreate + batched import). Run after the
# destructive importers and whenever the index drifts:
sudo -u dev bash -lc 'cd /srv/beta-claytontv/current && .venv/bin/python manage.py reindex_search'
```

> After changing `shared/.env`, restart the app so it reloads the env:
> `sudo systemctl restart gunicorn-claytontv-beta.service` (env is read once at
> worker start via `load_dotenv`).

Local dev: `docker compose up typesense` (repo-root `docker-compose.yml`) +
`uv run poe manage reindex_search`.

### Environment isolation

Use a separate Typesense instance and API key for each environment. The beta
example binds `127.0.0.1:8108`; reserve a different loopback port for dev
(e.g. `8109`) and production. Verify actual bindings with
`sudo docker ps --format '{{.Names}} {{.Ports}}'`.

`reindex_search` deletes and rebuilds the `content` collection. Applications
sharing an instance therefore share an index. Set each environment's
`TYPESENSE_HOST`, `TYPESENSE_PORT` and `TYPESENSE_API_KEY` explicitly; the
application's default port is `8108`.

All deployment callers enable reindexing, so each environment requires a
reachable, separately configured instance before deployment.

## Error pages

On-brand, self-contained (inline CSS + inline logo; no Vite/CDN/app context):

- **Django** (`DEBUG=False`): `templates/404.html`, `500.html`, `403.html` — the
  exact names Django's default handlers render, so no custom `handlerXXX` needed.
- **nginx upstream-down (502/503/504):** gunicorn is down so Django can't render;
  nginx serves `public/50x.html` (collected to `staticfiles_collected/50x.html`).
  Add to each vhost's `server` block (`sites-available/beta-claytontv` and
  `claytontv`), then `sudo nginx -t && sudo systemctl reload nginx`:

      error_page 502 503 504 /50x.html;
      location = /50x.html {
          internal;
          root /srv/beta-claytontv/current/staticfiles_collected;  # prod: /srv/claytontv/...
      }

# Deployment

Two environments on one server (`app03.tgo.dev`, Contabo, Ubuntu 24.04 — also
hosts unrelated PHP sites; mind the blast radius).

| | Production | Beta |
|---|---|---|
| URL | https://claytontv.co.uk | https://beta.claytontv.co.uk |
| Branch | `main` | `beta` |
| Workflow | deploy-to-production.yaml | deploy-to-beta.yaml |
| Root | /srv/claytontv | /srv/beta-claytontv |
| Service | gunicorn-claytontv.service (+.socket) | gunicorn-claytontv-beta.service (+.socket) |
| Socket | shared/run/claytontv.sock | shared/run/claytontv-beta.sock |
| Python | 3.12 via poetry (legacy) | 3.14 via uv |
| Database | postgres `claytontv` | postgres `claytontv_beta` (own role) |
| Redis | db 1 (implicit default) | db 2 (explicit REDIS_URL) |
| TLS | certbot, auto-renew | certbot, auto-renew |

Both use the same blue-green layout: `releases/<timestamp>` + `current`
symlink + `shared/{.env,media,logs,run}`; beta adds `shared/backups/` and its
deploy runs **pg_dump before migrate** (keeps last 7 dumps, last 5 releases).
Deploys run as the `dev` user, whose sudo is limited to restarting the two
gunicorn services (sudoers drop-ins `90-dev-gunicorn-restart`,
`91-dev-gunicorn-beta`).

## Beta deploy flow

Push to `beta` → GitHub Actions (`environment: beta`; secrets `SSH_HOST`,
`SSH_PORT`, `SSH_USER`, `SSH_PRIVATE_KEY`) → build assets on the runner →
rsync release → `uv sync --locked --no-dev` (uv auto-provisions CPython 3.14)
→ collectstatic → pg_dump backup → migrate → symlink swap → service restart →
HTTP 200 smoke test.

Manual deploy (emergency): mirror the workflow's remote script from a local
checkout; see the workflow file — it is the single source of truth.

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
`uv run poe manage reindex_search`. Prod is **not** wired yet — a later,
legacy-team-coordinated step.

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

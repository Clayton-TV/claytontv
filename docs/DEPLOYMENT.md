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

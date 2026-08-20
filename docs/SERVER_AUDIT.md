# Server audit — app03.tgo.dev (2026-06-12)

> **Historical snapshot — do not read as current state.** This is a
> point-in-time survey taken on **2026-06-12**, before the beta and dev
> environments were built out. Much of it has since been actioned (swap,
> fail2ban, SSH hardening, uv/CPython 3.14). Where it disagrees with
> [DEPLOYMENT.md](DEPLOYMENT.md), **DEPLOYMENT.md wins** — notably the Python
> row below ("no 3.14, no uv"), which describes the pre-migration production
> box, not today's. Kept for the findings/rationale trail.

Read-only survey ahead of Epic 1 (beta environment). Shared box: also serves
liley.co and tgo.dev (php8.4-fpm) — every change below must consider blast
radius beyond claytontv.

## Inventory

| Area | Current state |
|---|---|
| OS | Ubuntu 24.04.2 LTS (Noble), kernel 6.8.0-124, no reboot pending |
| Hardware | 4 vCPU, 5.8 GB RAM, 145 GB disk (10% used), **no swap** |
| Updates | **136 packages upgradable** (8 held back); unattended-upgrades active (security only); last manual apt run 2026-06-02 |
| Python | 3.12.3 (default) + 3.13 system; **no 3.14, no uv**; stray poetry in ~/.local/bin |
| Node | v22.16.0 system-wide |
| Web | nginx 1.24.0; vhosts: claytontv, liley.co, tgo.dev |
| App server | gunicorn via systemd (`gunicorn-claytontv.service` + socket), user `dev`, 3 workers, unix socket, blue-green at /srv/claytontv (current → releases/20260222164050 — **last deploy 22 Feb**) |
| Database | PostgreSQL 18 (localhost only), `claytontv` db exists |
| Cache | Redis (localhost only) |
| Jobs | supervisor installed and running, **no programs configured**; cron available |
| TLS | certbot + active renewal timer; certs: claytontv.co.uk (+www, valid to 22 Jul), liley.co. Both domains behind Cloudflare proxy |
| DNS | beta.claytontv.co.uk → Cloudflare (proxied) ✅ already resolving |
| Firewall | ufw active: deny-in default; allows 80,443 + 2202 only |
| fail2ban | **not installed** |
| SSH | socket-activated, listening on **both 22 and 2202** (22 blocked by ufw); effective config: **PasswordAuthentication yes** (50-cloud-init.conf wins include order), **PermitRootLogin yes** |

## Findings, by priority

### P0 — security hardening (before beta goes public)
1. **SSH password auth is effectively ON.** `/etc/ssh/sshd_config.d/50-cloud-init.conf`
   sets `PasswordAuthentication yes`; OpenSSH first-match wins and config.d is
   included before the main file. Fix: drop a `00-hardening.conf` (lexically
   first) with `PasswordAuthentication no`, `PermitRootLogin no`,
   `KbdInteractiveAuthentication no`; validate with `sshd -t` + `sshd -T`;
   keep an active session open during restart.
2. **No fail2ban.** Install with jails for sshd (port 2202) and nginx
   (req-limit/bad-bot once rate limiting is in place).
3. **ssh.socket also binds port 22** (ufw blocks it, but remove the belt-and-
   braces gap): drop the 22 ListenStream from the socket override.

### P1 — platform updates
4. **apt upgrade the 136 pending packages** + investigate the 8 held back;
   schedule a reboot window if kernel/libc move (other sites affected — brief
   downtime, pick a quiet hour).
5. **Add 2–4 GB swapfile** (6 GB RAM box running postgres+redis+nginx+gunicorn
   ×N sites; one OOM kill of postgres would hurt everything).
6. **Install uv** (system-wide or for the deploy user) and let it manage
   CPython 3.14 for the app — no deadsnakes PPA needed, matches local dev.
7. Remove the stray poetry from `~/.local/bin` once the new deploy lands
   (the old deploy workflow still expects it until then — leave in place).

### P2 — beta environment (the actual Epic 1 build-out)
8. New `beta-claytontv` deploy root at `/srv/beta-claytontv` (same
   blue-green layout), separate `.env`, separate postgres db
   (`claytontv_beta`) and role; gunicorn unit `gunicorn-claytontv-beta`
   (+socket) running as a service user (not `dev`).
9. nginx vhost `beta.claytontv.co.uk` → beta socket; certbot cert via HTTP-01
   (Cloudflare-proxied HTTP-01 works — the existing claytontv.co.uk cert
   renews through the proxy already). Optionally add basic-auth or a
   Cloudflare Access rule while beta is rough.
10. `deploy-to-beta.yaml` GitHub workflow off the `beta` branch: uv sync
    instead of poetry, **pg_dump backup step before migrate**, same
    release/symlink/cleanup flow. New deploy SSH key restricted to the beta
    user.
11. Background jobs: use the already-running **supervisor** for the SSR node
    service (if/when SSR goes default-on) and queue workers; cron (or
    systemd timers) for scheduled YouTube polling.
12. Observability: app wiring to sentry.tgo.dev + posthog.tgo.dev DSNs in the
    beta `.env` (separate Sentry project/PostHog instance recommended for
    beta vs prod).

### Notes / non-issues
- Postgres 18 and Redis are localhost-bound — correct.
- ufw default-deny posture is right; only 80/443/2202 exposed.
- certbot auto-renewal timer healthy.
- nginx config for prod claytontv is sane (static/media aliases, socket
  upstream). Beta vhost can be a close copy with HSTS + security headers
  added (and later backported to prod).
- Prod last deployed 22 Feb 2026 — the live site runs four-month-old code;
  irrelevant to us but worth knowing when comparing behaviour.

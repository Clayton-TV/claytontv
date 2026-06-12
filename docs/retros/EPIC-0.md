# Epic 0 retrospective — Foundations & toolchain (2026-06-12)

## What shipped
uv + Python 3.14 + Django 6; Inertia v3 (template-override bridge) with opt-in
SSR; test harness with factories, feature tests, a query-count regression
guard, and a 60% coverage gate; CI on uv; CLAUDE.md + living master plan.
Side quests that paid off: beta environment live with push-to-deploy, server
hardened (the SSH config was silently accepting passwords), Vimeo unlisted-hash
fix (~2,400 videos), homepage N+1 fix (15s+ → 80ms).

## What worked
- **Spike before commit.** Both stack risks (Django 6 on 3.14, Inertia v3
  adapter gap) were resolved in hours because we tested the risky assumption
  first instead of building on it.
- **Real data immediately.** Importing the full 9,244-video catalogue locally
  surfaced the duplicate topics, dead series links, and (via beta's postgres)
  the homepage N+1. Empty-database development would have hidden all of it.
- **Post-flight checks after infra changes.** The apt upgrade silently 500'd
  production via stale pooled DB connections; the health check caught it in
  minutes.

## What to carry into Epic 1 leftovers / Epic 2
1. **SQLite hides what Postgres punishes.** Performance-sensitive work gets
   verified against beta (or local postgres) before merge, not after.
2. **The serializer is part of the query budget.** Inertia prop serialization
   caused more queries than the view body. Lesson encoded in
   `video_card_props()` and a regression test; apply the same scrutiny to
   every new page.
3. **`CONN_HEALTH_CHECKS=True`** goes into production settings with the
   observability wiring — the prod 500 incident was avoidable.
4. **Screenshot verification of embeds needs `zoom`** (cross-origin iframes
   render black in full-page captures) — already in TESTING_NOTES, applies to
   every Epic review.
5. **Permission boundaries on shared infra are a feature.** Two denials
   (apt upgrade, reboot) were both correct calls on a box hosting other sites;
   plan quiet windows with Jamie rather than treating them as blockers.

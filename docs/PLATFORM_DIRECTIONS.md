# Content intake and growth decisions

## Current position

- The legacy-admin sync keeps the catalogue current while the old site remains
  available. It is transitional and unreliable; issue #366 adds retries.
- Studio already supports authenticated editors, URL and playlist intake,
  draft review, publishing and soft deletion.
- Enrichment proposes metadata without overwriting editor data. It improves
  search recall and remains non-public. Semantic search and transcript input
  are deferred in issue #201.
- The platform is single-tenant. There are no church-scoped records, roles or
  branding boundaries.

## Decision required before cutover

Choose the supported source of new content after the legacy-admin sync ends.

| Option | Delivery scope | Editorial control | Decision |
| --- | --- | --- | --- |
| Editor-led intake | Existing Studio URL/playlist flow; manual classification and review | Full | Baseline and fallback |
| Trusted-source polling | Scheduled YouTube playlist or RSS import into Studio drafts | Full after review | Preferred next capability |
| Contributor submission | Accounts, source ownership and moderation workflow | Central publication gate | Defer until a pilot contributor exists |
| Multi-church platform | Tenant model, scoped access/search, branding and operations | Per-tenant plus central policy | Out of scope for cutover |

Trusted-source polling should create drafts in the existing review queue. It
must identify source provenance, de-duplicate by canonical URL and never
publish without an editor action. Reuse the existing metadata and playlist
services; do not add a separate intake path.

## Editorial policy to settle

1. Which organisations or channels are trusted sources?
2. Does every imported item require review, or may defined sources publish
   automatically?
3. What metadata is mandatory before publication?
4. Who owns source approval and removal?

These answers define the intake implementation and operating load. Track the
chosen work as GitHub issues on the Delivery board.

## Deferred capabilities

AI may assist classification, transcript search and duplicate detection. It
must remain a suggestion mechanism: editors approve changes to public metadata.

Contributor accounts and multi-church hosting require an explicit product
decision. Neither should shape the current single-tenant schema prematurely.

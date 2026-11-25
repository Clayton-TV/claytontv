# Topic recategorisation

Issue #311 uses the editor-approved `topics-mergers` sheet, reconciled against
`data/legacy_rescue/lookups/topics.csv`. The reviewable legacy-ID mapping is
`catalogue/data/topic_reconciliation.csv`. Destination seed IDs are excluded:
seed IDs and legacy source IDs are separate namespaces and can collide.

Preview the database-specific plan before applying it:

```bash
uv run poe manage reconcile_topics
```

The preflight performs no writes or search requests. It stops on missing or
ambiguous identities unless an existing canonical topic or an explicit exact-name
alias proves the row was already handled. Apply only after reviewing the complete
output:

```bash
uv run poe manage reconcile_topics --apply
```

Take a database snapshot and pause catalogue imports and editing between the
preview and manual apply. The command does not lock changes made between those
two separate invocations.

Application is atomic and idempotent. It transfers all five topic relation tables,
deletes a source only after its relations are copied, and rebuilds search after the
database commit. If search is unavailable, the database remains applied and the
command reports this recovery step:

```bash
uv run poe manage reindex_search
```

Existing canonical summaries are retained. Conflicting sheet summaries for
Marriage, Men and Women, Sin, and Suffering are reported for later editorial
choice. Legacy `108` Education is mapped for future ingestion but excluded from
existing-data reconciliation because the current database cannot distinguish it
from legacy `169` Education. Human Sexuality and `misc.` use explicit exact-name
aliases because the legacy lookup has no IDs. The former Heaven spelling is an
explicit compatibility alias and old mapped topic URLs redirect to an existing
canonical topic.

Current relation provenance cannot be reconstructed from colliding primary keys.
This command preserves every existing association while merging its current topic
row; correcting historic mislinks requires a separate source replay audit. The dev
snapshot rehearsal leaves `Tough Texts` unchanged because it is outside the
approved mapping.

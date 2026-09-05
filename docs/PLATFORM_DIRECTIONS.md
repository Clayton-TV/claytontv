# Content intake

Studio supports authenticated editors, URL and playlist intake, draft review,
publishing and soft deletion. Use this workflow while replacing the temporary
legacy-admin sync.

## Cutover decision

Choose the source of new content before ending legacy sync:

| Source | Status | Requirement |
| --- | --- | --- |
| Editor-led intake | Existing baseline | Editors classify, review and publish |
| Trusted-source polling | Proposed next step | Import approved playlists or feeds into Studio drafts |
| Contributor submissions | Deferred | A named pilot, source ownership and moderation requirements |
| Multi-church hosting | Deferred | A separate product decision and tenancy design |

For polling, reuse existing metadata and playlist services. Record provenance,
de-duplicate canonical URLs and require editor publication.

Before implementation, agree trusted sources, required metadata and ownership
of source approval/removal. Track delivery in GitHub; this document defines no
additional implementation scope.

The current platform is single-tenant. Contributor accounts, tenancy and AI
workflows are outside the current scope.

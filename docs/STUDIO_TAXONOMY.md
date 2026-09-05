# Taxonomy maintenance

Use Django admin for infrequent speaker, series and topic corrections. Studio
already provides taxonomy selection when editing videos. Build a dedicated
maintenance screen only for a demonstrated recurring editorial need.

| Operation | Requirement |
| --- | --- |
| Edit a summary | Validate and save |
| Rename a record | Preserve references and update search |
| Merge records | Move relations, de-duplicate links, re-index affected videos and retain recovery information |

Merges must follow the importer's relations: speakers use `Video.speaker` and
series use `Series.videos`, not the unused `Video.series` foreign key.

Name similarity identifies review candidates, not proven duplicates. Show
linked videos and existing metadata so editors can establish identity before
merging. Do not build from historical candidate counts; check the target data
and agree the editor workflow in a GitHub issue first.

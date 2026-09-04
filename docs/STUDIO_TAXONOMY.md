# Studio taxonomy maintenance

## Scope

Taxonomy maintenance covers speakers, series and topics. Studio currently
offers taxonomy selection while editing videos. Django admin remains the
operational tool for rare corrections.

Build a dedicated Studio surface only when repeated editorial work justifies
it. Candidate detection is not a publication workflow.

## Operations

| Operation | Risk | Required behaviour |
| --- | --- | --- |
| Edit a series or topic summary | Low | Validate and save the field |
| Rename a record | Low | Preserve references and update search |
| Merge records | High | Move every relation, de-duplicate links, re-index affected videos and retain a recoverable audit trail |

The relation model differs by taxonomy. Speakers use the `Video.speaker` M2M;
series use `Series.videos`. Any merge must follow the importer’s relation,
not the unused `Video.series` foreign key.

## Candidate detection

Name similarity can prioritise review. It cannot establish identity. Show the
editor evidence needed to decide: linked videos, series, channels, dates and
existing metadata. Record a dismissed candidate so it is not repeatedly shown.

External or AI research may provide a suggestion only. It must not rename,
merge or create taxonomy records automatically.

## Delivery boundary

Do not build taxonomy management from historical candidate counts. Re-run
analysis against the target database before defining scope. Create a Delivery
board issue when a named editor workflow and its acceptance criteria are agreed.

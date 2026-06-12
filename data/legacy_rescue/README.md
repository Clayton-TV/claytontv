# Legacy data rescue (Epic 2.0) — findings & artifacts

Investigated 2026-06-12 against the full ctvDBreform legacy dump
(`programmes.json` + `series.json`, 9,496 programmes, 20,579 unique URLs).

## The headline: there was never a transcript archive to rescue

Every `transcript_link` (953) and `audio_link` (836) in the legacy dump is an
**external reference link**, not a hosted file:

| Destination | What it is |
|---|---|
| printandaudio.org.uk (incl. all bit.ly) | St Helen's-style sermon library — deep links to specific talks/search pages |
| desiringgod.org | 34 article/resource links |
| paultripp.com | 21 resource links |
| (one literal `27.10.17`) | data-entry garbage |

Consequences for the plan:
- **Transcript search comes from YouTube captions (Epic 4)** — there is no
  legacy transcript corpus to import.
- These links survive as "related resources" metadata; see
  `external_resource_links.csv`.

## What clayton.tv's dying server actually hosts

Of 20,579 URLs, only 127 reference clayton.tv: 114 internal page links inside
descriptions (useful for cutover redirect mapping, nothing to download) and 13
image files — **all already 404**, and the live legacy site itself now serves
YouTube-derived thumbnails. The 13 affected videos get fallback thumbnails via
the importer rework (#81). Video thumbnails otherwise live on i.ytimg.com /
img.youtube.com (4,699) and **i.vimeocdn.com (4,532 — tied to the Vimeo
account's health, not the legacy server**; relevant to the Vimeo account
audit).

## Artifacts

- `resolved_links.csv` — the 84 unique bit.ly short links resolved to their
  permanent printandaudio.org.uk destinations (bit.ly rot was the one genuine
  time-critical risk; defused). The recorded 403s are curl-UA bot blocking;
  the destinations return 200 to browsers.
- `external_resource_links.csv` — full per-programme mapping (1,788 rows:
  programme_id, ref, field, original_url, resolved_url) ready for the Epic 2
  importer to attach as related-resource metadata.

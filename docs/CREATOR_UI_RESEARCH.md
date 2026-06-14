# Creator / Editor UI — Design Research

*Drafted 2026-06-14 (Jamie + agent). Feeds the MVP2 implementation plan: "close
the old site." Opinionated and concrete to our stack — not a survey.*

> **Why this exists.** clayton.tv retires in a few months. When it does, the
> hourly legacy sync stops and the catalogue freezes. After that, **all content
> management happens in this app.** [docs/PLATFORM_DIRECTIONS.md](PLATFORM_DIRECTIONS.md)
> picks **Direction A — "The Trusted Library"** as the forced, near-term path:
> a modern intake to replace the legacy feed, plus *a pleasant custom
> content-management UI for non-technical editors* (Ettie's team) — explicitly
> separate from, and nicer than, the default Django `/admin`. This doc is the
> research behind both, plus the auth foundation (Epic 3) that gates them.

The shape of the answer, up front:

1. Build a small, focused **"Studio"** Inertia area (`/studio`) — not a
   general-purpose CMS. It needs ~6 screens, all in components we already ship.
2. **Intake is a paste box.** Paste a YouTube/Vimeo URL → we auto-fetch
   title/description/duration/thumbnail (we already have the YouTube key and the
   `harvest_durations` machinery) → the editor confirms metadata → save → it
   auto-indexes to Typesense via the existing signals.
3. Add a **`status` field to `Video`** (draft / published) — the one model change
   this requires — so intake can stage before it goes live, and so the future
   channel/RSS auto-import has a **review queue** to land in.
4. **Auth = stock Django auth + one custom Inertia login page + an "Editors"
   group.** Smallest real thing that works. Designed so contributor accounts
   (Direction B) and per-church tenancy (Direction C) slot in later without
   rework.

---

## 1. What makes a great editorial/CMS UI for non-technical users

I looked at the tools the brief names. The patterns below recur across all of
them; each is mapped to a concrete decision for our Studio.

### The patterns that matter (with sources)

**Content list as the home base — filterable table + bulk actions.**
Every good CMS opens on a *list of your stuff*, not a dashboard of widgets. Ghost
and YouTube Studio both default to "your content, newest first, with a status
column and a filter bar." Sanity Studio's list pane is the navigational spine of
the whole app — [Sanity's "missing UX guide"](https://www.mozestudio.com/journal/sanity-studio-the-missing-ux-guide)
stresses that a well-structured document list (grouped, filtered, ordered) is
*the* thing editors live in. Strapi gets dinged for the opposite: reviewers note
its admin "feels like a form builder rather than a publishing tool"
([Sanity vs Strapi vs Payload, 2026](https://dev.to/nayankyada/sanity-vs-strapi-vs-payload-cms-an-honest-comparison-for-2026-44li)).
*Lesson:* the list view is the product. Status, date, thumbnail, speaker,
quick-filter, search, select-many.

**Draft vs publish as a first-class, visible state.**
Sanity keeps drafts and published versions side by side and colour-codes the
toolbar so you always know what state you're in
([Content Releases](https://www.sanity.io/docs/studio/content-releases)). Ghost's
entire contributor model hinges on "draft → submitted → published." YouTube
Studio has Draft / Scheduled / Public visibility. *Lesson:* never let an editor
wonder "is this live?" A status pill on every row, and an explicit Publish
action distinct from Save.

**Autosave + reassurance, or explicit Save with clear feedback — pick one and
be loud about it.** Ghost and Sanity autosave continuously and show "Saved."
Editors trust the tool because they never lose work. If we *don't* autosave
(simpler), we must show an unmistakable success toast and a dirty-state guard
("you have unsaved changes"). *Lesson:* the cardinal sin is silent state. We
already have a `Toaster` + Django-messages→toast bridge — use it.

**Relationship pickers that search, not scroll.** The single biggest Django-admin
pain for our data: picking a speaker from ~600, a series from ~1,900, a topic
from a long list. Sanity/Payload use typeahead reference inputs. Django's
`filter_horizontal` (what `catalogue/admin.py` uses today) is a two-pane
multiselect that does not scale past a few dozen options. *Lesson:* every
relation picker is a **searchable combobox** — and we already have the exact
component (`reka-ui` Combobox / our `Command` primitive) powering the ⌘K palette.

**Media / URL embedding with live preview.** YouTube Studio shows the thumbnail
and a player the instant you have a video. *Lesson:* the moment a valid
YouTube/Vimeo URL is pasted, show the fetched thumbnail and metadata so the
editor *sees* they pasted the right thing before saving.

**Friendly, inline, field-level validation.** Inertia's documented pattern is
server-side validation flashed back as `errors` props rendered next to each
field ([Inertia Forms](https://inertiajs.com/docs/v2/the-basics/forms)).
Messages must be human ("That YouTube link is already in the library — [open it]")
not "`IntegrityError: UNIQUE constraint failed: catalogue_video.url`."

**Inline / quick edits from the list.** Common edits (change status, fix a
title, add a speaker) shouldn't always require opening the full editor. YouTube
Studio's hover-to-quick-edit and bulk-edit-from-selection are the gold standard
here. *Lesson:* a row "⋯" menu (Publish / Unpublish / Edit / Open on site) and a
bulk action bar when rows are selected.

**Keyboard + mobile as table stakes.** ⌘K to jump, `/` to search, escape to
close, full thumb-reachable controls and 16px inputs on mobile (we already
enforce the last two for the public site). Ettie may well add a talk from a
phone.

**Progressive disclosure.** Show the five fields that matter (URL, title,
speaker, series, status); fold the long tail (alt URLs, labels, Bible book,
audience, ministry) under "More details." This is the Master Plan's stated UX
principle (§3.4) and it's what separates Ghost's calm editor from Strapi's
wall-of-fields.

### Django-admin pain points to design *away from*

The current editorial home is the (nicely branded) Django `/admin`
([catalogue/admin.py](../catalogue/admin.py)). It works and should stay as the
power-tool / break-glass backstop — but it's wrong as the daily editor surface
for a non-technical volunteer, for reasons the wider community echoes
([Django Forum](https://forum.djangoproject.com/t/proper-architecture-for-django-cms-blog-interface-for-non-staff-users-content-post-writers/20282),
[django CMS reviews on G2](https://www.g2.com/products/django-cms/reviews)):

- **One-size-fits-all, dense, jargon-y.** Fieldset labels, raw model names, "id_number", choice codes.
- **`filter_horizontal` doesn't scale** to 600 speakers / 1,900 series — it's a scroll-and-hunt.
- **No paste-a-URL intake.** Every field is typed by hand; nothing is auto-fetched.
- **No friendly draft/publish.** There's no status concept at all today (see §3).
- **Validation surfaces as tracebacks / DB errors**, not guidance.
- **The decoy-relations trap is live in admin right now:** `VideoAdmin` exposes
  the `series` FK (line 37, 53–58 of admin.py) and the `ministry` M2M — both
  **never populated** by our importers (series membership lives on the
  `Series.videos` M2M; see [CLAUDE.md](../CLAUDE.md)). An editor using admin
  today will "link" a series via the FK and it will silently do nothing on the
  public site. Our Studio must use the *correct* relations.

**Verdict:** keep `/admin` for superusers and rare bulk/data fixes; build the
Studio as the everyday editorial surface.

---

## 2. Map to our stack

We are unusually well-positioned: the public site is already a polished
Inertia v3 + Vue 3 + Tailwind v4 app on `reka-ui`/shadcn-vue, and **most of the
hard parts of a CMS already exist as shipping code.**

### What we already have (reuse, don't rebuild)

| Need | Already in the repo |
|---|---|
| Searchable relation picker | `reka-ui` Combobox + our `ui/command/*` (powers ⌘K) — [CommandPalette.vue](../resources/js/components/organisms/CommandPalette.vue) |
| Modal / side editor | `ui/dialog/*` and `ui/sheet/*` (full sets exported) |
| Buttons / inputs / dropdowns / tooltips / skeletons | `ui/button`, `ui/input`, `ui/dropdown-menu`, `ui/tooltip`, `ui/skeleton` |
| Toasts for save/publish feedback | `organisms/Toaster.vue` + the Django-messages→`flash` bridge in [handle_inertia_requests.py](../app/http/middleware/handle_inertia_requests.py) |
| Video card / thumbnail render | `atoms/VideoCardItem.vue`, `app/cards.py::video_card_props` |
| Player preview | `organisms/PlayerFrame.vue` (`usePlayer` over YT iframe + Vimeo SDK) |
| Icons | `lucide-vue-next` |
| URL → metadata fetch | `catalogue/durations.py` (`youtube_id`, ISO-8601 parse, oEmbed) + `catalogue/youtube_live.py` (YouTube Data API client w/ retries) |
| Auto-index on save | `catalogue/search_signals.py` (`post_save`/`post_delete` → Typesense) |

Components the brief lists as "installed" that we'd add to the `ui/` set as we
go: **Tabs** (editor sections), **Card** (we have card-shaped molecules but not
a generic `ui/card`), **Table** (list view), **Badge** (status pills),
**Combobox** (relation pickers — reka-ui primitive, vendor like we did Command).
All are standard shadcn-vue registry pulls; we already vendor that way (the
Master Plan notes we fetch from the registry because we don't keep
`components.json`).

### Strict-encoder constraint (load-bearing)

Per [CLAUDE.md](../CLAUDE.md) and `app/views.py`: **never pass Video (or any
model) as an Inertia prop** — the serializer walks all five M2M relations and
recurses forever under SSR. Every Studio screen sends **plain dicts** (extend
`video_card_props` with a `status` field; add an `video_edit_props(video)` that
returns the editor's flat field set + the *currently selected* relation
ids/labels). Saves go the other way as a normal Inertia `POST`/`PATCH` to a thin
view → a plain service function → the model (the house style: thin views → service
→ models).

### Information architecture: the Studio

Mount everything under **`/studio`** (clear, on-brand, "where content gets made").
Gate the whole prefix behind login + the Editors group (§4). A minimal left rail
(or a top tab strip on mobile) with: **Library · Add · Review · Taxonomy**.

```
/studio                     → Library (the content list — the home base)
/studio/add                 → Add a video (the paste-a-URL intake)
/studio/video/<id>          → Edit a video (full editor)
/studio/review              → Review queue (drafts + future auto-imports)
/studio/taxonomy            → Manage speakers / series / topics (light CRUD)
/studio/login               → Custom Inertia login (public; §4)
```

**Why a separate area, not "admin polish"?** Direction A's brief is explicit:
*nicer than Django admin.* An Inertia area gives us our own design language, the
searchable pickers, the paste-intake, live preview, and the same calm
"media you can trust" feel as the public site — none of which `/admin` can do
without fighting it. It also means editors log into *one* product, not two.

### Screen-by-screen

**Library (`/studio`)** — the spine.
- A **Table** of videos: thumbnail · title · speaker(s) · series · date · a
  **status Badge** (Draft / Published) · runtime · a row `⋯` menu.
- A filter bar across the top: text search (hits the existing Typesense palette
  endpoint, scoped to videos), status filter (All / Published / Draft), and
  facet chips reusing `molecules/FilterChips.vue`.
- Row select → a **bulk action bar** (Publish, Unpublish, Delete-with-confirm).
- "Add a video" primary button top-right.
- Empty/loading states via `molecules/EmptyState.vue` + `ui/skeleton`.

**Add a video (`/studio/add`)** — see §3 in full. The headline screen.

**Edit a video (`/studio/video/<id>`)** — the full editor.
- **Tabs** or progressive sections: *Details* (title, description, status,
  date), *Classification* (speaker / series / topic / Bible book / audience /
  ministry — all searchable comboboxes), *Sources* (primary URL + `alternate_urls`),
  *Resources* (the `RelatedResource` inline, reusing the existing relation).
- A live **PlayerFrame** + thumbnail preview pinned alongside.
- Explicit **Save** (toast) and a **Publish/Unpublish** toggle. Dirty-state
  guard on navigate-away.
- Validation errors rendered inline per field (Inertia `errors` prop).

**Review queue (`/studio/review`)** — drafts awaiting a human.
- Same table as Library but filtered to `status=draft`, with the AI/auto-import
  provenance shown when it exists (future). Each row: *Approve & publish* /
  *Edit* / *Reject*. This is the surface that makes Direction A's "team reviews
  rather than types" real, and the exact place a future channel/RSS importer
  drops its finds (§3).

**Taxonomy (`/studio/taxonomy`)** — light CRUD for speakers/series/topics.
- Rename/merge speakers (we know there are name-variant dups), edit a series
  summary, fix a topic. Most of this is rare; keep it simple — a list + an edit
  Sheet. The `/admin` stays available for anything heavier.

---

## 3. Content intake flows

This is the urgent half of Direction A: a way for content to get *in*.

### The one model change: a `status` field on `Video`

There is **no published/draft/status field on `Video` today** — every imported
row is implicitly live. Intake and a review queue both need staging. Recommend:

```
status = models.CharField(
    max_length=12, default="published", db_index=True,
    choices=[("draft", "Draft"), ("published", "Published")],
)
```

- **Default `published`** so the ~13k existing rows keep showing after the
  migration (no behaviour change for legacy content). New intake defaults to
  `draft` until a human publishes.
- **Public views filter `status="published"`** — touch the `RECENT_FIRST`
  querysets in `app/views.py` (homepage `latest_videos`, latest feed, search
  hydration, browse pages). The Studio shows all statuses.
- **Search:** the Typesense doc should carry `status` (or we only index
  published docs). Cleanest: index everything with a `status` field and add a
  `filter_by:status:=published` on the *public* search/palette paths, leaving
  the Studio search unfiltered. The existing `search_signals` already re-index
  on every save, so a publish flip propagates in seconds for free.
- One-liner future-proofing: this same field is where a `"pending_review"` value
  slots in for Direction B's contributor flow.

Keep the change to **one field + one migration + the public-query filter**.
Resist adding scheduling/visibility tiers now (YAGNI for Direction A).

### Add a video — the paste-a-URL flow

The screen, step by step:

1. **Paste box.** One big input: "Paste a YouTube or Vimeo link." On a valid
   paste (debounced), fire a thin endpoint `POST /studio/api/fetch-metadata`.
2. **Auto-fetch** (server side — reuses what we already have):
   - `youtube_id(url)` / Vimeo detection — both already in
     [catalogue/durations.py](../catalogue/durations.py).
   - **YouTube:** one `videos.list?part=snippet,contentDetails` call (1 quota
     unit) via the existing client in
     [catalogue/youtube_live.py](../catalogue/youtube_live.py) — gives title,
     description, channel, thumbnail, and `contentDetails.duration` (parse with
     the existing `parse_iso8601_duration`). The key is already on beta.
   - **Vimeo:** the existing oEmbed call (no auth) — title, thumbnail, duration.
   - **Dedup check:** `Video.url` is unique; look up the pasted URL (and its id
     against `alternate_urls`) and, if found, return a friendly "already in the
     library — [open it]" instead of letting the save 500 on the constraint.
3. **Confirm & edit.** Pre-fill the editor form from the fetched data. Editor
   adjusts the title, writes/keeps the description, then sets the
   **classification** via searchable comboboxes: speaker(s), series, topic(s),
   Bible book(s), audience, ministry. (Use the **correct** relations — link
   series via `Series.videos.add(video)`, *not* the decoy FK.)
4. **Save.** Thin view → service function → model. New videos save as
   `draft` (land in Review) or publish immediately if the editor clicks Publish.
   On save, `search_signals` indexes it to Typesense automatically — no extra
   wiring.
5. **Thumbnail/duration backfill** is already covered: if the editor skips it,
   the nightly `harvest_durations` cron fills `duration_seconds` for anything
   null. Intake just front-loads it.

*Quota note (from PLATFORM_DIRECTIONS Appendix 3):* this is `videos.list`
(1 unit), **never** `search.list` (100 units). Cheap at any plausible add rate.

### Bulk add

Two realistic forms, both cheap to build on the same core:

- **Paste many URLs** (one per line / comma-separated) → fan out the same
  per-URL fetch (YouTube batches 50 ids per `videos.list` call — the
  `harvest_durations` code already batches this way) → land them all as
  **drafts in the Review queue** for classification. This is the manual bridge
  until the auto-importer exists.
- **Playlist / channel pull** (the seam to the future): paste a YouTube playlist
  or channel → enumerate its videos → drafts in Review. This is literally
  Direction A's "automated intake," done on-demand. Poll known playlists
  (~1 unit), not `search`.

### How future channel/RSS auto-import feeds the same queue

The Review queue is the integration point. A scheduled `import_from_sources`
command (Direction A, later) — polling trusted YouTube playlists and/or
Podcasting 2.0 / sermon RSS feeds — does exactly what the paste flow does
per-URL, but unattended, and writes rows as `status="draft"` with provenance
metadata. **Editors then see them in `/studio/review` and approve/tidy/publish.**
"AI proposes, human disposes" (Direction D) layers on by pre-filling the
classification fields as *suggestions* the reviewer accepts — the queue UI
doesn't change, only how full the draft arrives. Building the manual paste flow
first means the auto-importer has a finished review surface to target on day one.

---

## 4. Auth & roles (Epic 3)

Today there is **no login at all**: the Inertia shared `auth.user` is real-or-null
([handle_inertia_requests.py](../app/http/middleware/handle_inertia_requests.py)
— the placeholder "Test User" was already removed), nothing is route-protected,
and `/admin` is the only authenticated surface. We need the *smallest real thing*
that gates the Studio and sets up the future.

### Recommendation — stock Django auth + one Inertia login page + an Editors group

**Use Django's built-in auth wholesale.** No `AbstractUser` swap unless we have a
concrete reason — and we don't yet (email-as-username is the only likely want;
defer it). Django's `User`, `Group`, `login()`, session middleware, password
hashing, and rate-limit-friendly views are exactly right for a small team.

**Roles via one Group, not custom permission code:**
- **Superuser** (Jamie / a trusted admin): full `/admin`, everything.
- **"Editors" group**: members of this group can reach `/studio`. That's the
  whole model for Direction A. (Django's per-model permissions exist if we ever
  want finer control, but a single group is enough now.)
- Gate the Studio with a small decorator/mixin: `login_required` +
  `user.is_staff or user.groups.filter(name="Editors").exists()`. One helper,
  applied to every `/studio` view.

**Custom Inertia login page (`/studio/login`):**
- A real Vue page (not Django's admin login) so editors meet *our* design from
  the first screen — `ui/input`, `ui/button`, our logo, the calm look.
- POST to a thin Django view that calls `authenticate()` + `login()`, then
  `redirect()`s to `/studio` (Inertia treats the redirect as navigation).
- **Validation caveat (load-bearing):** inertia-django 1.2 has **no built-in
  error-bag sharing** — the upstream PR for it
  ([inertia-django#32](https://github.com/inertiajs/inertia-django/pull/32)) is
  unmerged, and issue
  [#49](https://github.com/inertiajs/inertia-django/issues/49) is exactly this
  question. So on a bad login we **`share(request, errors={...})` then re-render
  the login page** (or redirect back with the error in a flash, reusing the
  existing `flash` bridge). Wrap this in one tiny helper now; rip it out when
  upstream lands. Inertia's standard `useForm().errors` pattern then renders the
  message inline ([Inertia Forms](https://inertiajs.com/docs/v2/the-basics/forms)).
- Keep it boring and safe: Django's session cookie, CSRF already wired for
  Inertia POSTs, a sane password validator set, and lockout-on-repeat (e.g.
  `django-axes`) if we want it — but that's a "could," not a "must."

**Creating editor accounts (Direction A):** Jamie creates them in `/admin`
(create user → add to "Editors") and shares credentials, or a one-line
management command `create_editor <email>`. No self-signup — Direction A has no
public accounts. This is deliberately the RightNow/Laracasts model: curation is
the product, so the gate stays closed.

### How this sets up B and C (without building them now)

- **Direction B (contributors):** add a `"Contributors"` group (can reach
  `/studio/add` and their own drafts, **cannot publish**) and a
  `"pending_review"` video status. The Review queue already exists; publishing
  already gated. This is the well-trodden Ghost "submit, don't self-publish"
  model — and it's a *group + a status value*, not a rewrite.
- **Direction C (whitelabel/tenancy):** a future nullable `church`/`tenant` FK on
  `User` and on content models, with the Studio querysets scoped by the user's
  tenant. The relational model is clean enough to extend (PLATFORM_DIRECTIONS
  Appendix 1). **Don't** build tenancy now, but **do** keep the Studio's data
  access in service functions (`videos_for(user)`) rather than raw `Video.objects`
  in views — that single discipline is what makes adding a tenant scope a
  one-function change later. Stick to **subdomains + one shared DB** when the
  time comes; custom domains + per-tenant DBs are the small-team trap.

---

## 5. Recommended build sequence

Each slice ships to `beta` on its own PR, TDD, Claude-Preview-verified — the
established cadence. Ordered so the **legacy-retirement risk retires first**
(intake exists before the old feed dies) and auth lands exactly when the Studio
needs gating.

**Slice 0 — `Video.status` field (the unblock).**
One field, one migration (default `published`), filter public querysets +
search to published. No UI yet. Ships invisibly; everything else builds on it.
*Tests:* existing rows stay visible; a `draft` row is hidden from home/latest/
search/browse but reachable in admin.

**Slice 1 — Auth foundation (Epic 3).**
Django auth on, "Editors" group, the `/studio` gate helper, the custom Inertia
`/studio/login` page with the manual `errors` bridge, `create_editor` command.
Nothing behind it yet except a placeholder "Studio coming soon." *Tests:*
anonymous → redirected to login; non-editor → 403; editor → reaches `/studio`.

**Slice 2 — Studio Library (the list view).**
The content table: thumbnail/title/speaker/series/date/status, search + status
filter, row `⋯` (Publish/Unpublish/Edit/Open-on-site), bulk publish/unpublish.
Reuses the palette search endpoint, `FilterChips`, `Toaster`. This alone already
beats `/admin` for the daily "what's in the library / flip something live" job.

**Slice 3 — Add a video (paste-a-URL intake). The headline.**
The paste box → `fetch-metadata` endpoint (YouTube `videos.list` + Vimeo oEmbed,
reusing `durations.py`/`youtube_live.py`) → pre-filled editor with searchable
relation comboboxes (correct relations!) → save as draft/publish → auto-index.
Friendly dedup on the unique URL. **This is the slice that lets the team add
content without the legacy site** — the moment Direction A's floor is met.

**Slice 4 — Edit a video (full editor) + Review queue.**
The tabbed editor (Details / Classification / Sources / Resources) with live
preview and inline validation, plus `/studio/review` (drafts list with
Approve/Edit/Reject). Together these complete the manual editorial loop.

**Slice 5 — Bulk add + on-demand playlist/channel pull.**
Paste-many and "import a YouTube playlist" → drafts into Review. The manual
bridge to automation, and a useful tool in its own right.

**Slice 6 — Light taxonomy management (`/studio/taxonomy`).**
Rename/merge speakers, edit series/topic summaries. Lower priority; `/admin`
covers it until then.

**After MVP2 (not this phase, but designed-for):** the scheduled
`import_from_sources` auto-importer feeding the Review queue (Direction A
automation); AI-assisted pre-fill of draft classification (Direction D);
contributor accounts + `pending_review` (Direction B). All land on the
foundation the slices above create — no rework.

---

### One-paragraph summary for the plan

Build a focused **`/studio`** Inertia area — Library list, paste-a-URL Add,
full editor, Review queue, light taxonomy — entirely in components we already
ship (`reka-ui`/shadcn-vue Combobox, Dialog, Sheet, Tabs, Table, Badge, Button,
Toaster) and serving plain dicts (never models) per the strict encoder. The
intake reuses our existing YouTube Data API client + `harvest_durations`
machinery to auto-fill metadata from a pasted link, and saves auto-index to
Typesense via the signals already in place. The **one model change** is a
`status` (draft/published) field on `Video`, which also gives the future
auto-importer a **review queue** to land in. Gate it all with **stock Django
auth + a custom Inertia login + an "Editors" group** — the smallest real auth,
explicitly shaped so contributor roles (B) and per-church tenancy (C) are later
additions, not rewrites. Sequence the work so intake exists *before* the legacy
feed dies: `status` field → auth → Library → **Add (the headline)** → editor +
Review → bulk/playlist → taxonomy.

---

#### Sources

- Sanity Studio UX / drafts & releases: [missing UX guide](https://www.mozestudio.com/journal/sanity-studio-the-missing-ux-guide), [Content Releases](https://www.sanity.io/docs/studio/content-releases), [What's new Dec 2025](https://www.sanity.io/blog/what-s-new-december-2025)
- Headless CMS editor-UX comparisons (Strapi "form builder" critique, Payload developer-first): [Sanity vs Strapi vs Payload 2026](https://dev.to/nayankyada/sanity-vs-strapi-vs-payload-cms-an-honest-comparison-for-2026-44li), [Payload vs Strapi](https://punits.dev/blog/payloadcms-vs-strapi/)
- Django admin limits for non-technical editors: [Django Forum thread](https://forum.djangoproject.com/t/proper-architecture-for-django-cms-blog-interface-for-non-staff-users-content-post-writers/20282), [django CMS reviews (G2)](https://www.g2.com/products/django-cms/reviews)
- Inertia forms / validation pattern; inertia-django error-bag gap: [Inertia Forms](https://inertiajs.com/docs/v2/the-basics/forms), [Inertia Validation](https://inertiajs.com/validation), [inertia-django#32](https://github.com/inertiajs/inertia-django/pull/32), [inertia-django#49](https://github.com/inertiajs/inertia-django/issues/49)
- Internal: [docs/PLATFORM_DIRECTIONS.md](PLATFORM_DIRECTIONS.md), [docs/MASTER_PLAN.md](MASTER_PLAN.md), [CLAUDE.md](../CLAUDE.md), [app/views.py](../app/views.py), [catalogue/admin.py](../catalogue/admin.py), [catalogue/youtube_live.py](../catalogue/youtube_live.py), [catalogue/durations.py](../catalogue/durations.py), [catalogue/search_signals.py](../catalogue/search_signals.py)
</content>
</invoke>

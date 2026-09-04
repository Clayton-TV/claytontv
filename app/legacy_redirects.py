"""301 redirects from legacy clayton.tv URLs to the new routes — for cutover.

When the legacy site is switched off and clayton.tv points here, old inbound
links (bookmarks, search engines, the 100+ in-description links) must not break.
The dying site's watch URLs all end in ``.../0i0/<programme_id>/``:

    /new/0i0/<id>/
    /find/explore/<category-path>/0i0/<id>/
    /schedule/0i0/<id>

Our ``Video.id`` *is* that legacy programme id (the importer keyed off it), so
we 301 to ``/video/<id>`` when the programme is publicly available — and 404
otherwise (never 301 to the wrong content, which would mislead search engines).
"""

from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from catalogue.models.video import Video


def legacy_video_redirect(request, pid):
    """301 a legacy ``…/0i0/<pid>/`` watch URL to ``/video/<pid>``, or 404 if no
    public video has that id (draft / trashed / unknown all 404)."""
    if not Video.objects.published().filter(id=str(pid)).exists():
        raise Http404
    return redirect(reverse("video", args=[int(pid)]), permanent=True)

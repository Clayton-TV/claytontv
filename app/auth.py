"""Content-editing authorisation. Kept tiny and central so the Studio gate
(Slice 1) and the draft-visibility checks share one definition."""

EDITORS_GROUP = "Editors"


def can_edit_content(user):
    """True for users allowed to see/edit unpublished (draft) content and reach
    the Studio.

    Staff (superusers via Django ``/admin``) always qualify; Slice 1 (Epic 3)
    also admits members of the "Editors" group. Kept dependency-light — one
    authenticated check plus a single cheap group lookup.
    """
    return user.is_authenticated and (user.is_staff or user.groups.filter(name=EDITORS_GROUP).exists())

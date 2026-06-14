"""Content-editing authorisation. Kept tiny and central so the Studio gate
(Slice 1) and the draft-visibility checks share one definition."""


def can_edit_content(user):
    """True for users allowed to see/edit unpublished (draft) content.

    Slice 0: staff only (superusers via Django ``/admin``). Slice 1 (Epic 3)
    extends this to members of the "Editors" group.
    """
    return user.is_authenticated and user.is_staff

"""The Inertia prop encoder must reject raw models/querysets (which recurse on
our cyclic relations) and pass plain data through. See app/inertia_encoder.py.
"""

import json

import pytest

from app.inertia_encoder import StrictInertiaJsonEncoder
from catalogue.models.video import Video
from tests.factories import VideoFactory

pytestmark = pytest.mark.django_db


def dump(value):
    return json.dumps(value, cls=StrictInertiaJsonEncoder)


def test_rejects_a_bare_model():
    video = VideoFactory()
    with pytest.raises(TypeError, match="Inertia prop"):
        dump({"video": video})


def test_rejects_a_queryset():
    VideoFactory()
    with pytest.raises(TypeError, match="Inertia prop"):
        dump({"videos": Video.objects.all()})


def test_allows_plain_dicts_and_lists():
    payload = {"title": "Hi", "videos": [{"id": 1, "name": "A"}]}
    assert json.loads(dump(payload)) == payload
